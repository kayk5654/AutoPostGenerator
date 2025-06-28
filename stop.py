#!/usr/bin/env python3
"""
Stop script for Auto Post Generator

This script gracefully stops running Auto Post Generator instances.
It can stop both launcher-managed processes and standalone Streamlit processes.

Usage:
    python stop.py [options]
    
Examples:
    python stop.py                      # Stop all Auto Post Generator processes
    python stop.py --pid 12345          # Stop specific process by PID
    python stop.py --port 8501          # Stop process using specific port
    python stop.py --force              # Force kill processes
    python stop.py --docker             # Stop Docker containers
"""

import sys
import os
import argparse
import subprocess
import time
import signal
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import psutil
except ImportError:
    psutil = None

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


class ProcessStopper:
    """Handles stopping of Auto Post Generator processes."""
    
    def __init__(self):
        self.pid_file = PROJECT_ROOT / '.launcher.pid'
    
    def get_launcher_pid(self) -> Optional[int]:
        """Get PID from launcher PID file."""
        if not self.pid_file.exists():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Verify process still exists
            if psutil and psutil.pid_exists(pid):
                return pid
            else:
                # Clean up stale PID file
                self.cleanup_pid_file()
                return None
        except (ValueError, IOError):
            return None
    
    def cleanup_pid_file(self):
        """Remove launcher PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                print("🧹 Cleaned up stale PID file")
        except Exception as e:
            print(f"⚠️  Could not remove PID file: {e}")
    
    def find_streamlit_processes(self) -> List[Dict[str, Any]]:
        """Find all running Streamlit processes related to Auto Post Generator."""
        processes = []
        
        if not psutil:
            print("⚠️  psutil not available. Cannot find running processes automatically.")
            return processes
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = proc.info['cmdline'] or []
                    
                    # Look for Streamlit processes
                    if any('streamlit' in str(arg).lower() for arg in cmdline):
                        # Check if it's running our app.py
                        if any('app.py' in str(arg) for arg in cmdline):
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline,
                                'create_time': proc.info['create_time']
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"⚠️  Error scanning processes: {e}")
        
        return processes
    
    def find_process_by_port(self, port: int) -> Optional[Dict[str, Any]]:
        """Find process using a specific port."""
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
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        
        return None
    
    def stop_process(self, pid: int, force: bool = False, timeout: int = 10) -> bool:
        """Stop a process gracefully or forcefully."""
        if not psutil:
            print(f"⚠️  psutil not available. Trying basic kill for PID {pid}")
            try:
                if force:
                    os.kill(pid, signal.SIGKILL)
                else:
                    os.kill(pid, signal.SIGTERM)
                return True
            except (OSError, ProcessLookupError):
                return False
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            if force:
                print(f"🔥 Force killing process {process_name} (PID: {pid})")
                process.kill()
                process.wait(timeout=5)
            else:
                print(f"🛑 Gracefully stopping process {process_name} (PID: {pid})")
                process.terminate()
                
                try:
                    # Wait for graceful shutdown
                    process.wait(timeout=timeout)
                    print(f"✅ Process {pid} stopped gracefully")
                except psutil.TimeoutExpired:
                    print(f"⏰ Process {pid} didn't stop gracefully, force killing...")
                    process.kill()
                    process.wait(timeout=5)
                    print(f"🔥 Process {pid} force killed")
            
            return True
            
        except psutil.NoSuchProcess:
            print(f"ℹ️  Process {pid} already stopped")
            return True
        except psutil.AccessDenied:
            print(f"❌ Access denied when trying to stop process {pid}")
            return False
        except Exception as e:
            print(f"❌ Error stopping process {pid}: {e}")
            return False
    
    def stop_docker_containers(self) -> bool:
        """Stop Docker containers related to Auto Post Generator."""
        print("🐳 Stopping Docker containers...")
        
        # Check for docker-compose.yml
        docker_compose_file = PROJECT_ROOT / 'docker-compose.yml'
        
        success = True
        
        if docker_compose_file.exists():
            print("📋 Found docker-compose.yml, stopping services...")
            try:
                # Try docker-compose first
                result = subprocess.run(
                    ['docker-compose', 'down'],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✅ Docker Compose services stopped")
                else:
                    print(f"⚠️  Docker Compose stop had issues: {result.stderr}")
                    success = False
                    
            except subprocess.TimeoutExpired:
                print("⏰ Docker Compose stop timed out")
                success = False
            except FileNotFoundError:
                print("❌ docker-compose command not found")
                success = False
            except Exception as e:
                print(f"❌ Error stopping Docker Compose: {e}")
                success = False
        
        # Also try to stop any containers with our image name
        try:
            # Find containers with our image name
            result = subprocess.run(
                ['docker', 'ps', '-q', '--filter', 'ancestor=auto-post-generator'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                container_ids = result.stdout.strip().split('\n')
                for container_id in container_ids:
                    print(f"🛑 Stopping container {container_id}")
                    stop_result = subprocess.run(
                        ['docker', 'stop', container_id],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if stop_result.returncode == 0:
                        print(f"✅ Container {container_id} stopped")
                    else:
                        print(f"⚠️  Failed to stop container {container_id}")
                        success = False
            
        except subprocess.TimeoutExpired:
            print("⏰ Docker container stop timed out")
            success = False
        except FileNotFoundError:
            print("❌ docker command not found")
            success = False
        except Exception as e:
            print(f"❌ Error stopping Docker containers: {e}")
            success = False
        
        return success
    
    def cleanup_resources(self):
        """Clean up launcher resources."""
        print("🧹 Cleaning up resources...")
        
        # Remove PID file
        self.cleanup_pid_file()
        
        # Clean up log files if they exist
        log_files = [
            PROJECT_ROOT / 'launcher.log',
            PROJECT_ROOT / '.streamlit' / 'config.toml'
        ]
        
        for log_file in log_files:
            if log_file.exists():
                try:
                    # Don't actually delete logs, just mention them
                    print(f"📝 Log file: {log_file}")
                except Exception as e:
                    print(f"⚠️  Could not access {log_file}: {e}")
        
        print("✅ Resource cleanup completed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Stop Auto Post Generator processes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stop.py                      # Stop all Auto Post Generator processes
  python stop.py --pid 12345          # Stop specific process by PID
  python stop.py --port 8501          # Stop process using port 8501
  python stop.py --force              # Force kill all processes
  python stop.py --docker             # Stop Docker containers
  python stop.py --cleanup            # Only clean up resources

The script will:
1. Look for launcher-managed processes (via PID file)
2. Find Streamlit processes running app.py
3. Stop processes gracefully (SIGTERM) or forcefully (SIGKILL)
4. Clean up launcher resources
        """
    )
    
    parser.add_argument(
        '--pid',
        type=int,
        help='Stop specific process by PID'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='Stop process using specific port'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force kill processes (SIGKILL instead of SIGTERM)'
    )
    
    parser.add_argument(
        '--docker',
        action='store_true',
        help='Stop Docker containers'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Only perform cleanup, don\'t stop processes'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout for graceful shutdown (seconds, default: 10)'
    )
    
    args = parser.parse_args()
    
    stopper = ProcessStopper()
    
    print("🛑 Auto Post Generator Stop Script")
    print("=" * 40)
    
    # Handle cleanup-only mode
    if args.cleanup:
        stopper.cleanup_resources()
        return 0
    
    # Handle Docker mode
    if args.docker:
        success = stopper.stop_docker_containers()
        stopper.cleanup_resources()
        return 0 if success else 1
    
    stopped_any = False
    
    # Handle specific PID
    if args.pid:
        print(f"🎯 Stopping process with PID {args.pid}")
        if stopper.stop_process(args.pid, args.force, args.timeout):
            stopped_any = True
        else:
            print(f"❌ Failed to stop process {args.pid}")
            return 1
    
    # Handle specific port
    elif args.port:
        print(f"🎯 Looking for process using port {args.port}")
        proc_info = stopper.find_process_by_port(args.port)
        if proc_info:
            print(f"📍 Found process: {proc_info['name']} (PID: {proc_info['pid']})")
            if stopper.stop_process(proc_info['pid'], args.force, args.timeout):
                stopped_any = True
            else:
                print(f"❌ Failed to stop process {proc_info['pid']}")
                return 1
        else:
            print(f"ℹ️  No process found using port {args.port}")
    
    # Handle general case - stop all related processes
    else:
        # First, try to stop launcher-managed process
        launcher_pid = stopper.get_launcher_pid()
        if launcher_pid:
            print(f"🎯 Found launcher-managed process (PID: {launcher_pid})")
            if stopper.stop_process(launcher_pid, args.force, args.timeout):
                stopped_any = True
        
        # Then find and stop any other Streamlit processes
        streamlit_processes = stopper.find_streamlit_processes()
        
        if streamlit_processes:
            print(f"🔍 Found {len(streamlit_processes)} Streamlit process(es)")
            
            for proc in streamlit_processes:
                # Skip if we already stopped this process via launcher PID
                if launcher_pid and proc['pid'] == launcher_pid:
                    continue
                
                print(f"📍 Process: {proc['name']} (PID: {proc['pid']})")
                cmdline_str = ' '.join(proc['cmdline'][:3]) + '...' if len(proc['cmdline']) > 3 else ' '.join(proc['cmdline'])
                print(f"   Command: {cmdline_str}")
                
                if stopper.stop_process(proc['pid'], args.force, args.timeout):
                    stopped_any = True
        else:
            if not launcher_pid:
                print("ℹ️  No Auto Post Generator processes found running")
    
    # Cleanup resources
    stopper.cleanup_resources()
    
    if stopped_any:
        print("\n✅ Auto Post Generator processes stopped successfully")
        return 0
    else:
        if args.pid or args.port:
            return 1  # Specific target not found/stopped
        else:
            print("\nℹ️  No processes were running")
            return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Stop script interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Stop script failed: {e}")
        sys.exit(1)