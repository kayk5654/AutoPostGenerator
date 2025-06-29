#!/usr/bin/env python3
"""
Universal Python Launcher for Auto Post Generator

This launcher provides multiple execution modes for the Auto Post Generator:
- Development mode with auto-restart and debug features
- Production mode with optimized settings and monitoring
- Docker mode for containerized deployment

Usage:
    python run.py [mode] [options]
    
Examples:
    python run.py dev                    # Development mode
    python run.py production --port 8080 # Production on custom port
    python run.py docker                 # Docker mode
"""

import sys
import os
import argparse
import subprocess
import time
import logging
import signal
import socket
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile
import json

try:
    import psutil
except ImportError:
    psutil = None

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


class LauncherConfig:
    """Configuration management for the launcher."""
    
    DEFAULT_CONFIG = {
        'port': 8501,
        'host': 'localhost',
        'debug': False,
        'auto_restart': True,
        'log_level': 'INFO',
        'browser_auto_open': True,
        'file_watching': True,
        'headless': False,
        'max_upload_size': '200MB',
        'server_timeout': 30
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Load from config file if specified
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self.config.update(file_config)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_file}: {e}")
        
        # Override with environment variables
        env_mapping = {
            'APG_PORT': ('port', int),
            'APG_HOST': ('host', str),
            'APG_DEBUG': ('debug', lambda x: x.lower() in ('true', '1', 'yes')),
            'APG_LOG_LEVEL': ('log_level', str),
            'APG_AUTO_RESTART': ('auto_restart', lambda x: x.lower() in ('true', '1', 'yes')),
            'APG_HEADLESS': ('headless', lambda x: x.lower() in ('true', '1', 'yes'))
        }
        
        for env_var, (config_key, converter) in env_mapping.items():
            if env_var in os.environ:
                try:
                    self.config[config_key] = converter(os.environ[env_var])
                except ValueError as e:
                    print(f"Warning: Invalid value for {env_var}: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def update(self, updates: Dict[str, Any]):
        """Update configuration values."""
        self.config.update(updates)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate port
        port = self.config.get('port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append(f"Invalid port number: {port}")
        
        # Validate host
        host = self.config.get('host')
        if not isinstance(host, str) or not host.strip():
            errors.append(f"Invalid host address: {host}")
        
        # Validate log level
        log_level = self.config.get('log_level', '').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            errors.append(f"Invalid log level: {log_level}. Must be one of {valid_levels}")
        
        return errors


class EnvironmentManager:
    """Manages environment setup and validation."""
    
    @staticmethod
    def get_project_root() -> Path:
        """Get the project root directory."""
        return PROJECT_ROOT
    
    @staticmethod
    def find_virtual_env() -> Optional[Path]:
        """Find the virtual environment directory."""
        project_root = EnvironmentManager.get_project_root()
        
        # Check common venv locations
        venv_paths = [
            project_root / 'venv',
            project_root / '.venv',
            project_root / 'env',
            project_root / '.env'
        ]
        
        for venv_path in venv_paths:
            if venv_path.exists() and venv_path.is_dir():
                # Check if it's a valid virtual environment
                if platform.system() == 'Windows':
                    python_exe = venv_path / 'Scripts' / 'python.exe'
                else:
                    python_exe = venv_path / 'bin' / 'python'
                
                if python_exe.exists():
                    return venv_path
        
        return None
    
    @staticmethod
    def is_virtual_env_active() -> bool:
        """Check if a virtual environment is currently active."""
        return hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
    
    @staticmethod
    def activate_virtual_env() -> bool:
        """Activate virtual environment if found."""
        if EnvironmentManager.is_virtual_env_active():
            return True
        
        venv_path = EnvironmentManager.find_virtual_env()
        if not venv_path:
            return False
        
        # Add virtual environment to PATH
        if platform.system() == 'Windows':
            scripts_dir = venv_path / 'Scripts'
        else:
            scripts_dir = venv_path / 'bin'
        
        if scripts_dir.exists():
            current_path = os.environ.get('PATH', '')
            os.environ['PATH'] = f"{scripts_dir}{os.pathsep}{current_path}"
            os.environ['VIRTUAL_ENV'] = str(venv_path)
            return True
        
        return False
    
    @staticmethod
    def validate_environment() -> List[str]:
        """Validate the development environment."""
        errors = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            errors.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check for required files
        project_root = EnvironmentManager.get_project_root()
        required_files = ['app.py', 'requirements.txt']
        
        for file_name in required_files:
            file_path = project_root / file_name
            if not file_path.exists():
                errors.append(f"Required file not found: {file_path}")
        
        # Check for Streamlit
        try:
            import streamlit
        except ImportError:
            errors.append("Streamlit not installed. Run: pip install streamlit")
        
        return errors
    
    @staticmethod
    def check_dependencies() -> List[str]:
        """Check if all dependencies are installed."""
        missing = []
        
        required_modules = [
            'streamlit',
            'pandas',
            'openai',
            'google.generativeai',
            'anthropic'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        return missing


class PortManager:
    """Manages port availability and allocation."""
    
    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0
        except Exception:
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 8501, max_attempts: int = 100) -> Optional[int]:
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            if PortManager.is_port_available(port):
                return port
        return None
    
    @staticmethod
    def get_port_process_info(port: int) -> Optional[Dict[str, Any]]:
        """Get information about the process using a port."""
        if not psutil:
            return None
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            return {
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': proc.info['cmdline']
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        
        return None


class ProcessManager:
    """Manages application processes."""
    
    def __init__(self):
        self.pid_file = PROJECT_ROOT / '.launcher.pid'
        self.process = None
    
    def create_pid_file(self, pid: int):
        """Create PID file for process tracking."""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
        except Exception as e:
            print(f"Warning: Could not create PID file: {e}")
    
    def remove_pid_file(self):
        """Remove PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            print(f"Warning: Could not remove PID file: {e}")
    
    def get_running_pid(self) -> Optional[int]:
        """Get PID from PID file if it exists and process is running."""
        if not self.pid_file.exists():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            if psutil and psutil.pid_exists(pid):
                return pid
            else:
                # Clean up stale PID file
                self.remove_pid_file()
                return None
        except Exception:
            return None
    
    def find_streamlit_processes(self) -> List[Dict[str, Any]]:
        """Find running Streamlit processes."""
        processes = []
        
        if not psutil:
            return processes
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('streamlit' in str(arg) for arg in cmdline):
                        if any('app.py' in str(arg) for arg in cmdline):
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        
        return processes
    
    def stop_process(self, pid: int, timeout: int = 10) -> bool:
        """Stop a process gracefully."""
        if not psutil:
            return False
        
        try:
            process = psutil.Process(pid)
            
            # Send SIGTERM
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=timeout)
                return True
            except psutil.TimeoutExpired:
                # Force kill if still running
                process.kill()
                process.wait(timeout=5)
                return True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True  # Process already stopped
        except Exception:
            return False


class StreamlitConfigManager:
    """Manages Streamlit configuration for different modes."""
    
    @staticmethod
    def get_config_dir() -> Path:
        """Get Streamlit config directory."""
        config_dir = PROJECT_ROOT / '.streamlit'
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    @staticmethod
    def generate_config(mode: str, config: LauncherConfig) -> Dict[str, Any]:
        """Generate Streamlit configuration for the specified mode."""
        base_config = {
            'server.port': config.get('port'),
            'server.address': config.get('host'),
            'server.headless': config.get('headless'),
            'browser.gatherUsageStats': False
        }
        
        if mode == 'development':
            base_config.update({
                'server.runOnSave': config.get('auto_restart', True),
                'server.fileWatcherType': 'auto' if config.get('file_watching') else 'none',
                'logger.level': config.get('log_level', 'DEBUG').lower()
            })
        elif mode == 'production':
            base_config.update({
                'server.runOnSave': False,
                'server.fileWatcherType': 'none',
                'logger.level': 'info',
                'server.headless': True
            })
        elif mode == 'docker':
            base_config.update({
                'server.address': '0.0.0.0',
                'server.headless': True,
                'server.enableCORS': False,
                'server.enableXsrfProtection': False,
                'server.runOnSave': False,
                'server.fileWatcherType': 'none'
            })
        
        return base_config
    
    @staticmethod
    def write_config_file(config: Dict[str, Any]):
        """Write Streamlit configuration to file."""
        config_dir = StreamlitConfigManager.get_config_dir()
        config_file = config_dir / 'config.toml'
        
        try:
            with open(config_file, 'w') as f:
                f.write("# Auto-generated Streamlit configuration\n")
                f.write("# Generated by Auto Post Generator Launcher\n\n")
                
                for key, value in config.items():
                    if isinstance(value, bool):
                        value_str = str(value).lower()
                    elif isinstance(value, str):
                        value_str = f'"{value}"'
                    elif isinstance(value, (int, float)):
                        value_str = str(value)
                    else:
                        value_str = str(value)
                    
                    f.write(f'{key} = {value_str}\n')
        except Exception as e:
            print(f"Warning: Could not write Streamlit config: {e}")


class UniversalLauncher:
    """Main launcher class that orchestrates all functionality."""
    
    def __init__(self):
        self.config = None
        self.process_manager = ProcessManager()
        self.logger = None
    
    def setup_logging(self, log_level: str, mode: str):
        """Setup logging configuration."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if mode == 'development':
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format=log_format,
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler(PROJECT_ROOT / 'launcher.log')
                ]
            )
        else:
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format=log_format,
                handlers=[logging.StreamHandler(sys.stdout)]
            )
        
        self.logger = logging.getLogger('AutoPostGeneratorLauncher')
    
    def check_existing_instance(self) -> bool:
        """Check if another instance is already running."""
        existing_pid = self.process_manager.get_running_pid()
        if existing_pid:
            print(f"Another launcher instance is already running (PID: {existing_pid})")
            return True
        return False
    
    def pre_flight_checks(self) -> bool:
        """Perform pre-flight checks before launching."""
        print("🔍 Performing pre-flight checks...")
        
        # Check environment
        env_errors = EnvironmentManager.validate_environment()
        if env_errors:
            print("❌ Environment validation failed:")
            for error in env_errors:
                print(f"   - {error}")
            return False
        
        # Check dependencies
        missing_deps = EnvironmentManager.check_dependencies()
        if missing_deps:
            print("❌ Missing dependencies:")
            for dep in missing_deps:
                print(f"   - {dep}")
            print("\nInstall missing dependencies with: pip install -r requirements.txt")
            return False
        
        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            print("❌ Configuration validation failed:")
            for error in config_errors:
                print(f"   - {error}")
            return False
        
        # Check port availability
        port = self.config.get('port')
        host = self.config.get('host')
        
        if not PortManager.is_port_available(port, host):
            print(f"❌ Port {port} is already in use")
            
            # Try to find process using the port
            proc_info = PortManager.get_port_process_info(port)
            if proc_info:
                print(f"   Process using port: {proc_info['name']} (PID: {proc_info['pid']})")
            
            # Try to find alternative port
            alt_port = PortManager.find_available_port(port + 1)
            if alt_port:
                print(f"💡 Alternative port available: {alt_port}")
                user_input = input(f"Use port {alt_port} instead? (y/N): ").strip().lower()
                if user_input in ('y', 'yes'):
                    self.config.update({'port': alt_port})
                else:
                    return False
            else:
                return False
        
        print("✅ Pre-flight checks passed!")
        return True
    
    def run_development(self) -> int:
        """Run in development mode with auto-restart and debugging."""
        print("🚀 Starting Auto Post Generator in Development Mode")
        
        # Setup development environment
        os.environ['STREAMLIT_ENV'] = 'development'
        
        # Activate virtual environment
        if not EnvironmentManager.is_virtual_env_active():
            if EnvironmentManager.activate_virtual_env():
                print("✅ Virtual environment activated")
            else:
                print("⚠️  No virtual environment found")
        
        # Skip custom Streamlit config to avoid compatibility issues
        # Use command-line arguments instead
        
        # Build Streamlit command
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(self.config.get('port')),
            '--server.address', self.config.get('host'),
            '--browser.gatherUsageStats', 'false'
        ]
        
        if not self.config.get('browser_auto_open'):
            cmd.extend(['--server.headless', 'true'])
        
        try:
            print(f"📡 Starting on http://{self.config.get('host')}:{self.config.get('port')}")
            print("💡 Development mode features:")
            print("   - Auto-restart on file changes")
            print("   - Debug logging enabled")
            print("   - File watching enabled")
            print("\n🛑 Press Ctrl+C to stop\n")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Create PID file
            self.process_manager.create_pid_file(process.pid)
            
            # Stream output
            try:
                for line in process.stdout:
                    print(line.rstrip())
            except KeyboardInterrupt:
                print("\n🛑 Stopping development server...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            
            return process.returncode or 0
            
        except Exception as e:
            self.logger.error(f"Failed to start development server: {e}")
            return 1
        finally:
            self.process_manager.remove_pid_file()
    
    def run_production(self) -> int:
        """Run in production mode with optimized settings."""
        print("🏭 Starting Auto Post Generator in Production Mode")
        
        # Setup production environment
        os.environ['STREAMLIT_ENV'] = 'production'
        
        # Skip custom Streamlit config to avoid compatibility issues
        # Use command-line arguments instead
        
        # Build Streamlit command
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(self.config.get('port')),
            '--server.address', self.config.get('host'),
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ]
        
        try:
            print(f"📡 Starting on http://{self.config.get('host')}:{self.config.get('port')}")
            print("🏭 Production mode features:")
            print("   - Optimized performance")
            print("   - Headless operation")
            print("   - Production logging")
            print("\n🛑 Press Ctrl+C to stop\n")
            
            # Start process
            process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
            
            # Create PID file
            self.process_manager.create_pid_file(process.pid)
            
            # Wait for process
            try:
                return process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping production server...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                return 0
            
        except Exception as e:
            self.logger.error(f"Failed to start production server: {e}")
            return 1
        finally:
            self.process_manager.remove_pid_file()
    
    def run_docker(self) -> int:
        """Run in Docker mode."""
        print("🐳 Starting Auto Post Generator in Docker Mode")
        
        # Check if Docker is available
        docker_cmd = None
        for cmd in ['docker', 'podman']:
            if subprocess.run(['which', cmd], capture_output=True).returncode == 0:
                docker_cmd = cmd
                break
        
        if not docker_cmd:
            print("❌ Docker/Podman not found. Please install Docker to use Docker mode.")
            return 1
        
        # Skip custom Streamlit config to avoid compatibility issues
        # Use command-line arguments instead
        
        # Check for docker-compose.yml
        docker_compose_file = PROJECT_ROOT / 'docker-compose.yml'
        if docker_compose_file.exists():
            print("📋 Using docker-compose.yml configuration")
            cmd = [docker_cmd + '-compose', 'up']
        else:
            print("🐳 Using direct Docker execution")
            # Build Docker image if Dockerfile exists
            dockerfile = PROJECT_ROOT / 'Dockerfile'
            if dockerfile.exists():
                print("🔨 Building Docker image...")
                build_result = subprocess.run([
                    docker_cmd, 'build', '-t', 'auto-post-generator', '.'
                ], cwd=PROJECT_ROOT)
                
                if build_result.returncode != 0:
                    print("❌ Docker build failed")
                    return 1
                
                cmd = [
                    docker_cmd, 'run', '-it', '--rm',
                    '-p', f"{self.config.get('port')}:8501",
                    'auto-post-generator'
                ]
            else:
                print("❌ No Dockerfile found. Cannot run in Docker mode.")
                return 1
        
        try:
            print(f"📡 Docker container will be available on port {self.config.get('port')}")
            print("\n🛑 Press Ctrl+C to stop\n")
            
            # Start Docker container
            process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
            
            try:
                return process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping Docker container...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                return 0
            
        except Exception as e:
            self.logger.error(f"Failed to start Docker container: {e}")
            return 1
    
    def run(self, args: argparse.Namespace) -> int:
        """Main run method."""
        # Load configuration
        self.config = LauncherConfig(args.config)
        
        # Override config with command line arguments
        config_updates = {}
        if args.port:
            config_updates['port'] = args.port
        if args.host:
            config_updates['host'] = args.host
        if args.debug is not None:
            config_updates['debug'] = args.debug
        if hasattr(args, 'no_browser') and args.no_browser:
            config_updates['browser_auto_open'] = False
        
        self.config.update(config_updates)
        
        # Setup logging
        log_level = 'DEBUG' if self.config.get('debug') else self.config.get('log_level', 'INFO')
        self.setup_logging(log_level, args.mode)
        
        self.logger.info(f"Starting Auto Post Generator Launcher in {args.mode} mode")
        
        # Check for existing instance
        if self.check_existing_instance():
            return 1
        
        # Perform pre-flight checks
        if not self.pre_flight_checks():
            return 1
        
        # Route to appropriate mode
        if args.mode in ('dev', 'development'):
            return self.run_development()
        elif args.mode in ('prod', 'production'):
            return self.run_production()
        elif args.mode == 'docker':
            return self.run_docker()
        else:
            print(f"❌ Unknown mode: {args.mode}")
            return 1


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='Universal Python Launcher for Auto Post Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py dev                     # Development mode with auto-restart
  python run.py production              # Production mode
  python run.py docker                  # Docker mode
  python run.py dev --port 8080         # Custom port
  python run.py production --host 0.0.0.0 --no-browser  # Headless production

Modes:
  dev, development    Development mode with debugging and auto-restart
  prod, production    Production mode with optimized settings
  docker             Docker containerized mode

Environment Variables:
  APG_PORT           Override port (default: 8501)
  APG_HOST           Override host (default: localhost)
  APG_DEBUG          Enable debug mode (true/false)
  APG_LOG_LEVEL      Set log level (DEBUG/INFO/WARNING/ERROR)
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['dev', 'development', 'prod', 'production', 'docker'],
        help='Execution mode'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        help='Port to run on (default: 8501)'
    )
    
    parser.add_argument(
        '--host',
        help='Host address to bind to (default: localhost)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Disable automatic browser opening'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    return parser


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main() -> int:
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Create and run launcher
    launcher = UniversalLauncher()
    
    try:
        return launcher.run(args)
    except KeyboardInterrupt:
        print("\n🛑 Launcher interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Launcher failed with error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())