# User Guide

A comprehensive guide to using the Auto Post Generator application for creating AI-powered social media content.

## 🎯 Getting Started

### First-Time Setup

1. **Open the Application**
   - Navigate to the application URL in your web browser
   - You'll see the main interface with a 5-step workflow

2. **Understand the Workflow**
   The application follows a clear 5-step process:
   - 🤖 Configure LLM
   - 📁 Upload Files
   - ⚙️ Set Parameters
   - 🚀 Generate Posts
   - ✏️ Edit & Export

3. **Progress Tracking**
   - The top of the page shows your current progress
   - Completed steps are marked with ✅
   - Current step is marked with 🔄
   - Future steps are marked with ⏳

## 🤖 Step 1: Configure LLM Provider

### Choosing Your AI Provider

The application supports three major LLM providers:

#### OpenAI (GPT-3.5/GPT-4)
- **Best for**: General content, creative writing
- **API Key Format**: Starts with `sk-`
- **Getting Started**: Visit [platform.openai.com](https://platform.openai.com/api-keys)

#### Google Gemini
- **Best for**: Factual content, technical writing
- **API Key Format**: Starts with `AI`
- **Getting Started**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)

#### Anthropic Claude
- **Best for**: Long-form content, nuanced writing
- **API Key Format**: Starts with `sk-ant`
- **Getting Started**: Visit [Anthropic Console](https://console.anthropic.com/)

### API Key Setup

1. **Select Your Provider**
   - Choose from the dropdown menu
   - Each provider has different strengths

2. **Enter Your API Key**
   - Paste your API key into the password field
   - The application validates the format in real-time
   - ✅ Green checkmark = valid format
   - ❌ Red error = invalid format

3. **Security Note**
   - API keys are only used for your session
   - They are never stored permanently
   - They are automatically filtered from logs

## 📁 Step 2: Upload Files

### Source Files (Required)

Upload files containing the content you want to share:

#### Supported Formats
- **Text Files (.txt)**: Plain text content
- **Markdown (.md)**: Formatted text with markdown
- **Word Documents (.docx)**: Microsoft Word documents
- **PDF Files (.pdf)**: Portable document format

#### Best Practices
- **Clear Content**: Ensure files contain well-structured information
- **Key Information**: Include important details you want highlighted
- **Multiple Files**: Combine different sources for richer content
- **File Size**: Keep files under 10MB for optimal performance

#### Examples of Good Source Files
- Product announcements
- Blog posts
- Press releases
- Feature descriptions
- Company updates
- Research findings

### Brand Guide (Optional)

Upload your brand guidelines to ensure consistent voice:

#### What to Include
- **Voice and Tone**: Professional, casual, friendly, etc.
- **Messaging Guidelines**: Key themes and messages
- **Do's and Don'ts**: What to avoid in messaging
- **Style Examples**: Sample content that represents your brand
- **Industry Terms**: Specific terminology to use

#### Example Brand Guide Content
```markdown
# Brand Voice Guidelines

## Tone
- Professional yet approachable
- Innovative and forward-thinking
- Customer-focused

## Messaging Principles
- Always lead with customer benefits
- Use clear, jargon-free language
- Include data and evidence when possible

## Avoid
- Technical jargon without explanation
- Controversial political topics
- Overly promotional language
```

### Post History (Optional)

Upload examples of your successful posts for style learning:

#### Required Format
Excel file (.xlsx) with these columns:
- **Post Text**: Your previous post content
- **Platform**: Target platform (X, LinkedIn, etc.)
- **Date**: Publication date (optional)

#### Benefits
- AI learns your successful patterns
- Maintains consistency with your existing content
- Improves engagement potential
- Adapts to your audience preferences

#### Example Post History
| Post Text | Platform | Date |
|-----------|----------|------|
| "Excited to announce our new feature that helps teams collaborate better! 🚀 #innovation" | LinkedIn | 2024-01-15 |
| "5 tips for better productivity in remote work..." | X | 2024-01-14 |

## ⚙️ Step 3: Set Parameters

### Basic Settings

#### Number of Posts
- **Range**: 1-50 posts per generation
- **Recommendation**: Start with 5-10 posts
- **Performance**: Larger batches take longer and use more API credits

#### Target Platform
Choose the platform where you'll publish:

##### X (Twitter)
- **Character Limit**: 280 characters
- **Style**: Concise, engaging, hashtag-friendly
- **Best For**: Quick updates, news, engagement

##### LinkedIn
- **Character Limit**: 3,000 characters
- **Style**: Professional, informative, industry-focused
- **Best For**: Business updates, thought leadership, networking

##### Facebook
- **Character Limit**: 63,206 characters
- **Style**: Conversational, community-focused
- **Best For**: Community engagement, detailed updates

##### Instagram
- **Character Limit**: 2,200 characters
- **Style**: Visual-first, lifestyle-focused
- **Best For**: Brand storytelling, visual content

### Advanced Options

Click "🔧 Advanced Options" to access detailed customization:

#### Generation Settings

##### Creativity Level
- **Conservative**: Safe, proven content approaches
- **Balanced**: Mix of creativity and safety (recommended)
- **Creative**: More innovative and unique content
- **Innovative**: Maximum creativity and originality

##### Content Preferences
- **Include Hashtags**: Automatic relevant hashtag generation
- **Include Emojis**: Add emojis for engagement and personality
- **Include Call-to-Action**: Add engagement prompts

#### Content Tone Options
- **Professional**: Business-focused, formal language
- **Casual**: Relaxed, conversational tone
- **Friendly**: Warm, approachable communication
- **Authoritative**: Expert, confident positioning
- **Inspirational**: Motivational, uplifting content

#### Safety Settings
- **Avoid Controversial Topics**: Skip sensitive subjects
- **Content Safety**: Follow platform community guidelines

## 🚀 Step 4: Generate Posts

### Generation Process

1. **Validation Check**
   - The application validates all inputs before generation
   - ❌ Red errors must be fixed before proceeding
   - ⚠️ Yellow warnings are recommendations

2. **Click Generate**
   - Large green "🚀 Generate Posts" button when ready
   - Progress bar shows generation stages
   - Estimated time: 10-30 seconds depending on settings

3. **Generation Stages**
   - 📄 Processing uploaded files
   - 🧠 Initializing AI model
   - ✍️ Generating creative content
   - 🎯 Optimizing for platform
   - ✨ Finalizing posts

### What Happens During Generation

1. **File Processing**
   - Extracts text from uploaded files
   - Combines content from multiple sources
   - Applies encoding and formatting corrections

2. **Brand Integration**
   - Incorporates brand voice guidelines
   - Learns from post history examples
   - Applies tone and style preferences

3. **AI Generation**
   - Builds comprehensive prompt with all requirements
   - Calls your chosen LLM provider
   - Generates platform-optimized content

4. **Post Processing**
   - Validates generated content
   - Checks character limits
   - Formats for final presentation

## ✏️ Step 5: Edit and Export

### Post Management Interface

Once generation is complete, you'll see:

#### Individual Post Editing
- **Text Areas**: Edit each post directly
- **Real-time Validation**: Character count and limit checking
- **Auto-save**: Changes are saved automatically

#### Post Actions
- **🗑️ Delete**: Remove unwanted posts
- **↑ Up / ↓ Down**: Reorder posts
- **📋 Copy**: Copy individual posts to clipboard

#### Content Validation
- **Character Limits**: Platform-specific validation
- **Empty Posts**: Detection and warnings
- **Quality Checks**: Content validation

### Post Management Summary

View key metrics:
- **Total Posts**: Number of posts in your set
- **Empty Posts**: Posts that need content
- **Over Limit**: Posts exceeding platform limits

### Export Options

#### Quick Export
- **📄 Export to CSV**: Download all posts as CSV
- **📋 Copy All Posts**: Copy all posts to clipboard

#### Advanced Export Options

Click "🔧 Export Options" for detailed control:

##### Metadata Options
- **Include Metadata**: Add platform, post number, character count columns
- **Show Export Preview**: Preview CSV data before download

##### Technical Settings
- **File Encoding**: UTF-8, UTF-16, or ISO-8859-1
- **Timestamp Format**: ISO 8601, RFC 3339, or Human Readable

#### Export Formats

##### Standard CSV
```csv
post_text,generation_timestamp
"Your post content here","2024-01-15T10:30:00"
"Another post with content","2024-01-15T10:30:00"
```

##### CSV with Metadata
```csv
post_text,generation_timestamp,platform,post_number,character_count
"Your post content","2024-01-15T10:30:00","LinkedIn",1,145
"Another post","2024-01-15T10:30:00","LinkedIn",2,198
```

## 💡 Tips for Better Results

### Content Optimization

#### Source Files
- **Be Specific**: Include detailed information about what you want to share
- **Structure Well**: Use clear headings and organization
- **Include Context**: Explain why the information matters
- **Multiple Perspectives**: Combine different types of content

#### Brand Guidelines
- **Be Detailed**: More specific guidelines = better consistency
- **Include Examples**: Show what good content looks like
- **Define Voice**: Clear personality and tone descriptions
- **Set Boundaries**: Specify what to avoid

#### Post History
- **Use Best Posts**: Include your most successful content
- **Vary Examples**: Show different types of posts
- **Recent Content**: Include recent posts for current style
- **Platform-Specific**: Match examples to target platform

### Platform-Specific Tips

#### X (Twitter) Optimization
- Keep posts under 280 characters
- Use 1-2 relevant hashtags
- Include engaging hooks
- Ask questions for engagement
- Use threading for longer content

#### LinkedIn Optimization
- Professional tone and language
- Include industry insights
- Use professional hashtags
- Tag relevant companies/people
- Share valuable information

#### Facebook Optimization
- Conversational and engaging tone
- Ask questions to drive engagement
- Use emojis for personality
- Keep paragraphs short
- Include community-focused content

#### Instagram Optimization
- Visual-first mindset
- Use 5-10 relevant hashtags
- Engaging and lifestyle-focused
- Include calls-to-action
- Tell stories through captions

### Advanced Strategies

#### A/B Testing
- Generate multiple versions of similar content
- Test different tones and approaches
- Compare performance across variations
- Refine based on results

#### Content Series
- Generate related posts for campaigns
- Create consistent themes
- Build narrative across multiple posts
- Maintain brand consistency

#### Seasonal Content
- Include seasonal context in source files
- Adjust tone for holidays/events
- Consider timing in content strategy
- Plan ahead for key dates

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Generation Fails
**Problem**: Posts don't generate successfully
**Solutions**:
- Check API key validity and credits
- Reduce number of posts requested
- Simplify source content
- Try different LLM provider
- Check internet connection

#### Poor Quality Posts
**Problem**: Generated posts don't meet expectations
**Solutions**:
- Improve source file quality and detail
- Add comprehensive brand guidelines
- Include better post history examples
- Adjust creativity level
- Refine advanced settings

#### Character Limit Issues
**Problem**: Posts exceed platform limits
**Solutions**:
- Use the built-in editing interface
- Adjust creativity level to "Conservative"
- Include character limit guidance in brand guide
- Edit posts manually after generation

#### File Upload Problems
**Problem**: Can't upload files or files won't process
**Solutions**:
- Check file format (txt, md, docx, pdf only)
- Ensure file size is under 10MB
- Verify file isn't corrupted
- Try converting to different format
- Check file encoding (UTF-8 recommended)

#### API Key Issues
**Problem**: API key not working
**Solutions**:
- Verify key format matches provider requirements
- Check API key hasn't expired
- Ensure sufficient credits/quota
- Try regenerating API key
- Contact provider support

### Performance Tips

#### Faster Generation
- Use smaller files (< 1MB)
- Reduce post count (< 10)
- Choose "Conservative" creativity level
- Simplify advanced settings

#### Better Reliability
- Use stable internet connection
- Keep browser tab active during generation
- Don't close browser during processing
- Save work frequently

#### Memory Optimization
- Close other browser tabs
- Use latest browser version
- Clear browser cache if needed
- Restart browser for long sessions

## 📞 Getting Help

### In-App Help
- **💡 Tips for Better Results**: Contextual guidance throughout the app
- **Help Text**: Hover over question marks for field-specific help
- **Validation Messages**: Real-time feedback on inputs

### Documentation
- **User Guide**: This comprehensive guide
- **API Reference**: Technical documentation
- **Troubleshooting Guide**: Common issues and solutions
- **Deployment Guide**: Setup and configuration

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and references
- **Community**: GitHub Discussions for questions and ideas

---

**Happy posting! 🚀**