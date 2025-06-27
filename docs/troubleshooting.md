# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Auto Post Generator application.

## 🔍 Diagnostic Tools

### Application Health Check

1. **Check Application Status**
   ```bash
   curl http://localhost:8501/_stcore/health
   ```
   Expected response: `{"status": "ok"}`

2. **Check Logs**
   ```bash
   tail -f logs/app.log
   ```

3. **Monitor Resource Usage**
   ```bash
   # Memory usage
   ps aux | grep streamlit
   
   # Disk space
   df -h
   
   # Network connectivity
   ping api.openai.com
   ```

## 🔑 API Key Issues

### Problem: "Invalid API Key" Error

#### Symptoms
- ❌ Red error message during API key validation
- Authentication failures during generation
- "Invalid API key" errors in logs

#### Diagnosis
1. **Check API Key Format**
   - OpenAI: Must start with `sk-`
   - Google Gemini: Must start with `AI`
   - Anthropic: Must start with `sk-ant-`

2. **Verify Key Length**
   - OpenAI: Usually 51 characters
   - Google Gemini: Usually 39 characters
   - Anthropic: Usually 108 characters

3. **Test API Key Manually**
   ```bash
   # OpenAI
   curl https://api.openai.com/v1/models \\
     -H "Authorization: Bearer YOUR_API_KEY"
   
   # Google Gemini
   curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"
   
   # Anthropic
   curl https://api.anthropic.com/v1/messages \\
     -H "x-api-key: YOUR_API_KEY" \\
     -H "Content-Type: application/json"
   ```

#### Solutions
1. **Regenerate API Key**
   - Visit your provider's console
   - Create a new API key
   - Update the key in the application

2. **Check Key Permissions**
   - Ensure API key has necessary permissions
   - Verify account is in good standing
   - Check for usage restrictions

3. **Verify Account Status**
   - Check billing status
   - Ensure account isn't suspended
   - Verify sufficient credits/quota

### Problem: "Rate Limit Exceeded" Error

#### Symptoms
- ⏰ Rate limit error messages
- Generation fails after starting
- "Too many requests" in logs

#### Diagnosis
1. **Check Current Usage**
   - Review provider dashboard
   - Check recent API calls
   - Monitor rate limit headers

2. **Identify Usage Patterns**
   ```bash
   # Check recent generation attempts
   grep "rate limit" logs/app.log
   ```

#### Solutions
1. **Wait and Retry**
   - Wait for rate limit reset (usually 1 minute to 1 hour)
   - Reduce generation frequency
   - Space out requests

2. **Reduce Request Size**
   - Generate fewer posts per request
   - Split large batches into smaller ones
   - Use shorter content

3. **Upgrade Account**
   - Increase rate limits with paid plans
   - Contact provider for limit increases
   - Consider multiple API keys for different use cases

## 📁 File Upload Issues

### Problem: "Unsupported File Format" Error

#### Symptoms
- 📁 File format error during upload
- Files not processing correctly
- "Unsupported file type" messages

#### Diagnosis
1. **Check File Extension**
   - Supported: .txt, .md, .docx, .pdf, .xlsx (for history)
   - Case-sensitive on some systems

2. **Verify File Contents**
   ```bash
   file your_file.txt
   head -n 5 your_file.txt
   ```

#### Solutions
1. **Convert File Format**
   - Save Word documents as .docx (not .doc)
   - Export PDFs from original source
   - Save text files with .txt extension

2. **Check File Encoding**
   ```bash
   # Check file encoding
   file -bi your_file.txt
   
   # Convert encoding if needed
   iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt
   ```

3. **Rename File**
   - Ensure correct file extension
   - Remove special characters from filename
   - Use lowercase extensions

### Problem: "File Too Large" Error

#### Symptoms
- 📁 File size error during upload
- Upload progress stops
- "File too large" warnings

#### Diagnosis
1. **Check File Size**
   ```bash
   ls -lh your_file.pdf
   du -h your_file.pdf
   ```

2. **Identify Large Content**
   - Images embedded in documents
   - Excessive formatting
   - Large tables or datasets

#### Solutions
1. **Reduce File Size**
   - Remove images from documents
   - Simplify formatting
   - Split large files into smaller ones

2. **Optimize Content**
   - Extract text-only versions
   - Remove unnecessary sections
   - Compress PDFs before upload

3. **Alternative Approaches**
   - Copy/paste text content directly
   - Create summary documents
   - Use multiple smaller files

### Problem: "Cannot Read File" Error

#### Symptoms
- FileReadError exceptions
- Encoding errors in logs
- Corrupted content extraction

#### Diagnosis
1. **Check File Integrity**
   ```bash
   # For PDFs
   pdfinfo your_file.pdf
   
   # For Word docs
   file your_file.docx
   
   # For text files
   head your_file.txt
   ```

2. **Test File Opening**
   - Try opening in original application
   - Check for password protection
   - Verify file isn't corrupted

#### Solutions
1. **Fix File Issues**
   - Remove password protection
   - Re-save from original application
   - Export to different format

2. **Encoding Issues**
   - Save text files as UTF-8
   - Avoid special characters in content
   - Use plain text when possible

## 🚀 Generation Issues

### Problem: Generation Fails or Times Out

#### Symptoms
- ⏱️ Request timeout errors
- Generation never completes
- "Generation failed" messages

#### Diagnosis
1. **Check Network Connection**
   ```bash
   ping api.openai.com
   traceroute api.openai.com
   ```

2. **Review Generation Parameters**
   - Number of posts requested
   - Content complexity
   - Advanced settings

3. **Monitor System Resources**
   ```bash
   top
   free -h
   ```

#### Solutions
1. **Reduce Generation Complexity**
   - Generate fewer posts (1-5 instead of 20-50)
   - Simplify source content
   - Use conservative creativity level

2. **Improve Network**
   - Check internet connection stability
   - Disable VPN if causing issues
   - Try different network

3. **System Optimization**
   - Close other applications
   - Restart browser
   - Clear browser cache

### Problem: Poor Quality Generated Posts

#### Symptoms
- Posts don't match expectations
- Content seems generic
- Brand voice not reflected

#### Diagnosis
1. **Review Input Quality**
   - Check source file content
   - Evaluate brand guide detail
   - Assess post history examples

2. **Analyze Generation Settings**
   - Creativity level setting
   - Advanced options configuration
   - Platform-specific requirements

#### Solutions
1. **Improve Input Files**
   - Add more detailed source content
   - Create comprehensive brand guidelines
   - Include better post history examples

2. **Adjust Settings**
   - Try different creativity levels
   - Modify advanced settings
   - Experiment with different providers

3. **Iterative Improvement**
   - Generate small batches for testing
   - Refine inputs based on results
   - A/B test different approaches

## 🔧 Application Issues

### Problem: Application Won't Start

#### Symptoms
- Browser shows connection error
- Streamlit not accessible
- Application crashes on startup

#### Diagnosis
1. **Check Process Status**
   ```bash
   ps aux | grep streamlit
   netstat -tulpn | grep 8501
   ```

2. **Review Startup Logs**
   ```bash
   tail -f logs/app.log
   ```

3. **Verify Dependencies**
   ```bash
   pip list
   python -c "import streamlit; print(streamlit.__version__)"
   ```

#### Solutions
1. **Restart Application**
   ```bash
   # Kill existing process
   pkill -f streamlit
   
   # Restart application
   streamlit run app.py
   ```

2. **Fix Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install --upgrade streamlit
   ```

3. **Check Port Availability**
   ```bash
   # Use different port if 8501 is busy
   streamlit run app.py --server.port 8502
   ```

### Problem: Memory Issues

#### Symptoms
- Application becomes slow
- Browser tab becomes unresponsive
- Out of memory errors

#### Diagnosis
1. **Monitor Memory Usage**
   ```bash
   # System memory
   free -h
   
   # Process memory
   ps aux --sort=-%mem | head
   ```

2. **Check Browser Performance**
   - Open browser developer tools
   - Monitor memory tab
   - Check for memory leaks

#### Solutions
1. **Optimize Usage**
   - Process smaller files
   - Generate fewer posts at once
   - Close unused browser tabs

2. **System Cleanup**
   ```bash
   # Clear system cache
   sync && echo 3 > /proc/sys/vm/drop_caches
   
   # Restart application
   streamlit run app.py
   ```

3. **Browser Optimization**
   - Use latest browser version
   - Clear browser cache
   - Disable unnecessary extensions

## 🌐 Network Issues

### Problem: Connection Timeouts

#### Symptoms
- 🌐 Network error messages
- Long delays during generation
- Connection refused errors

#### Diagnosis
1. **Test Connectivity**
   ```bash
   # Test general connectivity
   ping google.com
   
   # Test API endpoints
   curl -I https://api.openai.com
   curl -I https://generativelanguage.googleapis.com
   ```

2. **Check DNS Resolution**
   ```bash
   nslookup api.openai.com
   dig api.openai.com
   ```

#### Solutions
1. **Network Troubleshooting**
   - Restart network connection
   - Try different DNS servers (8.8.8.8, 1.1.1.1)
   - Disable VPN temporarily

2. **Firewall Configuration**
   - Check firewall rules
   - Allow outbound HTTPS (443)
   - Whitelist API endpoints

3. **Proxy Settings**
   - Configure proxy if needed
   - Set environment variables:
     ```bash
     export https_proxy=http://proxy:port
     export http_proxy=http://proxy:port
     ```

## 💾 Data and Export Issues

### Problem: Export Fails

#### Symptoms
- ❌ CSV export doesn't work
- Download button not responding
- Corrupted export files

#### Diagnosis
1. **Check Generated Posts**
   - Verify posts contain content
   - Check for special characters
   - Review character counts

2. **Browser Compatibility**
   - Test in different browser
   - Check download settings
   - Verify popup blockers

#### Solutions
1. **Fix Post Content**
   - Remove or escape special characters
   - Ensure posts have content
   - Check character encoding

2. **Browser Settings**
   - Allow downloads from site
   - Disable popup blockers
   - Clear browser cache

3. **Alternative Export**
   - Use "Copy All Posts" option
   - Save content manually
   - Try different browser

### Problem: Character Encoding Issues

#### Symptoms
- Special characters display incorrectly
- Emojis not showing properly
- Foreign language text corrupted

#### Diagnosis
1. **Check File Encoding**
   ```bash
   file -bi input_file.txt
   ```

2. **Test Character Display**
   - View content in text editor
   - Check browser character encoding
   - Verify font support

#### Solutions
1. **Fix Input Encoding**
   ```bash
   # Convert to UTF-8
   iconv -f windows-1252 -t utf-8 input.txt > output.txt
   ```

2. **Browser Settings**
   - Set page encoding to UTF-8
   - Use fonts that support special characters
   - Update browser if needed

## 🔍 Advanced Debugging

### Enable Debug Logging

1. **Set Debug Level**
   ```bash
   export LOG_LEVEL=DEBUG
   streamlit run app.py
   ```

2. **Enable Verbose Output**
   ```bash
   streamlit run app.py --logger.level debug
   ```

### Capture Network Traffic

1. **Using Browser Developer Tools**
   - Open Network tab
   - Monitor API requests
   - Check response codes and timing

2. **Using Command Line**
   ```bash
   # Monitor network calls
   tcpdump -i any host api.openai.com
   ```

### Performance Profiling

1. **Memory Profiling**
   ```python
   import psutil
   import time
   
   def monitor_memory():
       process = psutil.Process()
       return process.memory_info().rss / 1024 / 1024  # MB
   ```

2. **Timing Analysis**
   ```python
   import time
   
   start_time = time.time()
   # Your operation here
   elapsed = time.time() - start_time
   print(f"Operation took {elapsed:.2f} seconds")
   ```

## 📊 Monitoring and Alerts

### Health Monitoring

1. **Application Health Check**
   ```bash
   #!/bin/bash
   # health_check.sh
   response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/_stcore/health)
   if [ $response != "200" ]; then
       echo "Application unhealthy: HTTP $response"
       exit 1
   fi
   echo "Application healthy"
   ```

2. **Log Monitoring**
   ```bash
   # Monitor for errors
   tail -f logs/app.log | grep -i error
   
   # Count error rates
   grep -c "ERROR" logs/app.log
   ```

### Automated Alerts

1. **Error Rate Monitoring**
   ```bash
   #!/bin/bash
   # error_alert.sh
   error_count=$(grep -c "ERROR" logs/app.log)
   if [ $error_count -gt 10 ]; then
       echo "High error rate detected: $error_count errors"
       # Send alert notification
   fi
   ```

2. **Resource Monitoring**
   ```bash
   #!/bin/bash
   # resource_alert.sh
   memory_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
   if (( $(echo "$memory_usage > 90" | bc -l) )); then
       echo "High memory usage: ${memory_usage}%"
   fi
   ```

## 🆘 Getting Help

### Information to Gather

When seeking help, please provide:

1. **Error Details**
   - Exact error message
   - Steps to reproduce
   - Expected vs actual behavior

2. **Environment Information**
   ```bash
   # System info
   uname -a
   python --version
   pip list | grep streamlit
   
   # Application logs
   tail -50 logs/app.log
   ```

3. **Configuration**
   - Browser type and version
   - Operating system
   - Network environment (corporate, home, etc.)

### Support Channels

1. **Self-Service**
   - Check this troubleshooting guide
   - Review application logs
   - Search existing issues

2. **Community Support**
   - GitHub Discussions for questions
   - Stack Overflow with relevant tags
   - Community forums

3. **Bug Reports**
   - GitHub Issues for bugs
   - Include reproduction steps
   - Attach relevant logs

### Emergency Procedures

1. **Application Down**
   ```bash
   # Quick restart
   pkill -f streamlit && streamlit run app.py
   ```

2. **Data Recovery**
   - Check browser session storage
   - Review temporary files
   - Use backup data if available

3. **Rollback Procedure**
   ```bash
   # Revert to previous version
   git checkout previous-working-commit
   streamlit run app.py
   ```

---

**Remember: Most issues can be resolved with basic troubleshooting. Start with the simple solutions before moving to complex diagnostics.**