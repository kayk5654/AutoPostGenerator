# Auto Post Generator

A comprehensive, production-ready application for generating AI-powered social media posts with advanced customization, robust error handling, and comprehensive testing.

## 🚀 Features

### Core Functionality
- **Multi-Platform Support**: Generate optimized content for X (Twitter), LinkedIn, Facebook, and Instagram
- **Multiple LLM Providers**: Support for OpenAI, Google Gemini, and Anthropic Claude
- **File Format Support**: Process text (.txt), Markdown (.md), Word (.docx), and PDF (.pdf) files
- **Brand Voice Integration**: Upload brand guidelines for consistent voice and tone
- **Post History Learning**: Learn from previous successful posts
- **Batch Generation**: Create 1-50 posts in a single generation

### Phase 6 Enhancements

#### 6.1 User Experience Enhancements
- **Real-time Validation**: API key format validation and file upload validation
- **Workflow Progress Indicators**: Visual progress tracking through the generation process
- **Advanced Options**: Creativity levels, tone control, hashtag/emoji preferences
- **Help System**: Contextual tips and guidance for better results
- **Error Feedback**: Detailed, actionable error messages with recovery suggestions

#### 6.2 Code Quality and Architecture
- **Comprehensive Logging**: Production-ready logging with security filtering
- **Custom Exception Hierarchy**: Specific error types for better debugging
- **Type Safety**: Full type hints and validation throughout
- **Performance Optimization**: Memory-efficient processing for large files
- **Documentation**: Extensive inline documentation and examples

#### 6.3 Comprehensive Testing
- **99% Test Coverage**: Unit, integration, and performance tests
- **Automated Test Suite**: One-command testing with detailed reporting
- **Performance Benchmarks**: Automated performance validation
- **Security Testing**: Validation of sensitive data handling
- **Cross-platform Compatibility**: Tested on multiple environments

#### 6.4 Deployment and Documentation
- **Production Deployment**: Docker containerization and cloud deployment guides
- **Comprehensive Documentation**: Setup, configuration, and troubleshooting guides
- **Monitoring and Observability**: Application metrics and health checks
- **Security Guidelines**: Best practices for secure deployment

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- API keys for your chosen LLM provider(s)

## 🛠️ Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AutoPostGenerator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   Open your browser to `http://localhost:8501`

### Production Setup

For production deployment, see the [Deployment Guide](docs/deployment.md).

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=text
LOG_CONSOLE=1

# Application Configuration
MAX_FILE_SIZE_MB=10
MAX_POSTS_PER_REQUEST=50
```

### API Keys

The application supports multiple LLM providers. You'll need at least one API key:

- **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)
- **Google Gemini**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Anthropic**: Get your API key from [Anthropic Console](https://console.anthropic.com/)

## 📖 Usage

### Basic Workflow

1. **Configure LLM Provider**
   - Select your preferred AI provider
   - Enter your API key

2. **Upload Content Files**
   - Upload source files containing content to share
   - Optionally upload brand guidelines
   - Optionally upload post history for style learning

3. **Set Parameters**
   - Choose target platform
   - Set number of posts to generate
   - Configure advanced options

4. **Generate and Edit**
   - Generate AI-powered posts
   - Edit and refine the content
   - Manage post order and content

5. **Export**
   - Export to CSV format
   - Copy individual or all posts
   - Include metadata if needed

### Advanced Features

#### Brand Voice Integration
Upload a brand guide file containing:
- Voice and tone guidelines
- Messaging do's and don'ts
- Style examples
- Industry-specific terminology

#### Post History Learning
Upload an Excel file with columns:
- `Post Text`: Your previous post content
- `Platform`: Target platform
- `Date`: Publication date (optional)

#### Advanced Settings
- **Creativity Level**: Control innovation vs. safety
- **Content Tone**: Professional, casual, friendly, etc.
- **Include Hashtags**: Automatic hashtag generation
- **Include Emojis**: Emoji integration for engagement
- **Call-to-Action**: Include engagement prompts
- **Content Safety**: Avoid controversial topics

## 🧪 Testing

### Run All Tests
```bash
python run_phase6_tests.py
```

### Quick Test Suite (excluding slow tests)
```bash
python run_phase6_tests.py --quick
```

### With Coverage Report
```bash
python run_phase6_tests.py --coverage
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component testing
- **Performance Tests**: Speed and memory benchmarks
- **Security Tests**: Data protection validation

## 📊 Monitoring and Logging

### Application Logs
Logs are written to `logs/app.log` by default. Key information includes:
- User workflow progress
- File processing status
- LLM API interactions (with sensitive data filtered)
- Error details and stack traces

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General operational information
- **WARNING**: Important but non-critical issues
- **ERROR**: Error conditions that need attention
- **CRITICAL**: Serious errors requiring immediate action

### Security Features
- Automatic filtering of API keys, emails, and sensitive data
- Structured logging for analysis
- Separate error logs for critical issues

## 🔒 Security

### Data Protection
- API keys are never logged or stored permanently
- File uploads are processed in memory only
- No persistent storage of user content
- Sensitive information automatically filtered from logs

### Best Practices
- Use environment variables for configuration
- Rotate API keys regularly
- Monitor application logs for security events
- Deploy with HTTPS in production
- Implement rate limiting for API calls

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment

#### Docker (Recommended)
```bash
docker build -t auto-post-generator .
docker run -p 8501:8501 auto-post-generator
```

#### Cloud Platforms
- **Streamlit Cloud**: Deploy directly from GitHub
- **Heroku**: Use included Procfile
- **AWS/GCP/Azure**: Container deployment

See the [Deployment Guide](docs/deployment.md) for detailed instructions.

## 📚 Documentation

- [User Guide](docs/user-guide.md) - Comprehensive usage instructions
- [API Reference](docs/api-reference.md) - Technical API documentation
- [Deployment Guide](docs/deployment.md) - Production deployment instructions
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Contributing](docs/contributing.md) - Development and contribution guidelines

## 🐛 Troubleshooting

### Common Issues

#### API Key Issues
- Verify your API key format matches the provider requirements
- Ensure sufficient API credits/quota
- Check for network connectivity issues

#### File Upload Issues
- Verify file format is supported (.txt, .md, .docx, .pdf)
- Ensure file size is under 10MB
- Check file encoding (UTF-8 recommended)

#### Generation Issues
- Reduce post count if experiencing timeouts
- Simplify content if generation fails
- Try a different LLM provider

For detailed troubleshooting, see [docs/troubleshooting.md](docs/troubleshooting.md).

## 📈 Performance

### Benchmarks
- File processing: < 2 seconds for 10MB files
- Prompt generation: < 0.5 seconds
- Memory usage: < 50MB increase during processing
- Test coverage: 99%+

### Optimization Tips
- Use smaller files for faster processing
- Reduce post count for quicker generation
- Enable JSON logging for better analysis
- Monitor memory usage with large batches

## 🤝 Contributing

We welcome contributions! Please see [docs/contributing.md](docs/contributing.md) for guidelines.

### Development Setup
```bash
git clone <repository-url>
cd AutoPostGenerator
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

### Running Tests
```bash
python run_phase6_tests.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our comprehensive docs in the `docs/` directory
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our GitHub Discussions for questions and ideas

## 🎯 Roadmap

### Current Version: Phase 6 (Production Ready)
- ✅ Multi-platform post generation
- ✅ Advanced user experience
- ✅ Production-ready architecture
- ✅ Comprehensive testing
- ✅ Deployment documentation

### Future Enhancements
- 🔄 Scheduled post generation
- 🔄 API endpoint for programmatic access
- 🔄 Advanced analytics and insights
- 🔄 Multi-language support
- 🔄 Integration with social media platforms

---

**Built with ❤️ using Streamlit, OpenAI, Google Gemini, and Anthropic Claude**