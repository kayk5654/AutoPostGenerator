# Universal Python Launcher Guide

The Auto Post Generator includes a powerful Universal Python Launcher that simplifies running the application across different environments and platforms.

## 🚀 Quick Start

### Simple Usage (Cross-Platform)

**Development Mode (Recommended for local development):**
```bash
# Windows
run.bat

# Linux/macOS
./run.sh

# Direct Python
python run.py dev
```

**Production Mode:**
```bash
# Windows
run.bat production

# Linux/macOS
./run.sh production

# Direct Python
python run.py production
```

**Docker Mode:**
```bash
# Windows
run.bat docker

# Linux/macOS
./run.sh docker

# Direct Python
python run.py docker
```

## 📋 Available Modes

### Development Mode (`dev` / `development`)
- **Auto-restart** on file changes
- **Debug logging** enabled
- **File watching** for hot reloading
- **Browser auto-open** (optional)
- **Enhanced error messages**

```bash
python run.py dev
python run.py dev --port 8080 --debug
```

### Production Mode (`prod` / `production`)
- **Optimized performance**
- **Headless operation** (no browser auto-open)
- **Production logging**
- **Resource optimization**
- **Monitoring-ready**

```bash
python run.py production
python run.py production --host 0.0.0.0 --port 80
```

### Docker Mode (`docker`)
- **Containerized execution**
- **Health checks**
- **Container lifecycle management**
- **Docker Compose support**

```bash
python run.py docker
```

## ⚙️ Configuration Options

### Command Line Arguments

```bash
python run.py [mode] [options]

Options:
  --port, -p PORT       Port to run on (default: 8501)
  --host HOST           Host address (default: localhost)
  --debug               Enable debug mode
  --no-browser          Disable browser auto-open
  --config CONFIG       Path to config file
```

### Environment Variables

Override settings using environment variables:

```bash
export APG_PORT=8080              # Custom port
export APG_HOST=0.0.0.0           # Bind to all interfaces
export APG_DEBUG=true             # Enable debug mode
export APG_LOG_LEVEL=DEBUG        # Set log level
export APG_AUTO_RESTART=false     # Disable auto-restart
export APG_HEADLESS=true          # Force headless mode
```

### Configuration File

Create a `config.json` file for persistent settings:

```json
{
  "port": 8501,
  "host": "localhost",
  "debug": false,
  "auto_restart": true,
  "log_level": "INFO",
  "browser_auto_open": true,
  "headless": false,
  "max_upload_size": "200MB"
}
```

Use with: `python run.py dev --config config.json`

## 🛑 Stopping the Application

### Quick Stop

```bash
# Windows
stop.bat

# Linux/macOS
./stop.sh

# Direct Python
python stop.py
```

### Advanced Stop Options

```bash
# Stop specific process by PID
python stop.py --pid 12345

# Stop process using specific port
python stop.py --port 8501

# Force kill (immediate termination)
python stop.py --force

# Stop Docker containers
python stop.py --docker

# Cleanup only (no process stopping)
python stop.py --cleanup
```

## 🔧 Features

### ✅ Environment Management
- **Automatic virtual environment detection and activation**
- **Dependency validation**
- **Python version checking**
- **Cross-platform compatibility**

### ✅ Process Management
- **PID file tracking**
- **Graceful shutdown handling**
- **Process discovery and monitoring**
- **Multiple instance prevention**

### ✅ Port Management
- **Automatic port availability checking**
- **Alternative port suggestions**
- **Port conflict resolution**
- **Process-to-port mapping**

### ✅ Configuration Management
- **Multiple configuration sources** (CLI → ENV → File → Defaults)
- **Configuration validation**
- **Environment-specific settings**
- **Hot configuration reloading**

### ✅ Streamlit Integration
- **Mode-specific Streamlit configurations**
- **Automatic config file generation**
- **Development and production optimizations**
- **Docker-ready settings**

## 🛠️ Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
❌ Port 8501 is already in use
   Process using port: streamlit (PID: 12345)
💡 Alternative port available: 8502
Use port 8502 instead? (y/N): y
```

**2. Missing Dependencies**
```bash
❌ Missing dependencies:
   - streamlit
   - pandas

Install missing dependencies with: pip install -r requirements.txt
```

**3. Python Version Issues**
```bash
❌ Python 3.8+ required, found 3.7.9
```

**4. Virtual Environment Not Found**
```bash
⚠️  No virtual environment found. Using system Python.
Consider creating a virtual environment with: python -m venv venv
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
python run.py dev --debug

# Or with environment variable
export APG_DEBUG=true
python run.py dev
```

### Log Files

Logs are written to:
- **Development mode**: `launcher.log` + console output
- **Production mode**: Console output only
- **Docker mode**: Container logs

## 🧪 Testing

### Test the Launcher

```bash
# Run launcher tests
python run_phase7_tests.py

# Run specific test categories
python run_phase7_tests.py --mode unit
python run_phase7_tests.py --mode integration
python run_phase7_tests.py --mode fast

# Run with coverage
python run_phase7_tests.py --coverage
```

### Validate Installation

```bash
# Check if launcher works
python run.py --help

# Test pre-flight checks
python run.py dev --no-browser
# Press Ctrl+C immediately to test startup
```

## 📦 Integration Examples

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Test Application Startup
  run: |
    timeout 30s python run.py production --no-browser || true
    python stop.py --cleanup
```

### Docker Deployment

```dockerfile
# Use the launcher in Docker
COPY run.py .
COPY stop.py .
CMD ["python", "run.py", "docker"]
```

### Systemd Service

```ini
[Unit]
Description=Auto Post Generator
After=network.target

[Service]
Type=exec
User=autopostgen
WorkingDirectory=/opt/autopostgen
ExecStart=/opt/autopostgen/run.py production --host 0.0.0.0
ExecStop=/opt/autopostgen/stop.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔐 Security Considerations

- **Never run as root** in production
- **Bind to localhost** unless external access is needed
- **Use virtual environments** to isolate dependencies
- **Monitor logs** for suspicious activity
- **Keep dependencies updated**

## 🚀 Advanced Usage

### Custom Configuration

```python
# Create custom launcher config
from run import LauncherConfig

config = LauncherConfig()
config.update({
    'port': 8080,
    'debug': True,
    'custom_setting': 'value'
})
```

### Health Checks

```bash
# Check if app is running
curl http://localhost:8501/_stcore/health

# Check specific port
python stop.py --port 8501 || echo "Port available"
```

### Monitoring Integration

```bash
# Get process information
python -c "
from run import ProcessManager
pm = ProcessManager()
processes = pm.find_streamlit_processes()
print(f'Found {len(processes)} processes')
"
```

## 📞 Support

If you encounter issues:

1. **Check the logs** for specific error messages
2. **Run with debug mode** for detailed output
3. **Verify dependencies** are installed correctly
4. **Check port availability** 
5. **Review the troubleshooting section** above

For additional help, refer to the main project documentation or create an issue in the project repository.