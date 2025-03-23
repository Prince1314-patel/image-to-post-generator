# 🎨 Image to Post Generator

A Streamlit app that transforms your images into engaging social media content using AI. Upload any image and get AI-generated captions, content, and relevant hashtags optimized for Instagram.

![App Demo](demo.gif)

## ✨ Features

- 📸 Image upload support (JPG, JPEG, PNG)
- 🤖 AI-powered image analysis
- ✍️ Generates engaging, medium-length content
- 🏷️ Creates relevant hashtags
- 📊 Real-time progress tracking
- 🎯 Instagram-optimized output

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/image-to-post-generator.git
cd image-to-post-generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
- Create a `.env` file in the root directory
- Add your API keys:
```
GROQ_API_KEY=your_groq_api_key
```

5. Run the app:
```bash
streamlit run main.py
```

## 📦 Requirements

- Python 3.8+
- Streamlit
- Pillow
- Groq
- python-dotenv
- httpx

## 🛠️ Project Structure

```
image-to-post-generator/
├── main.py           # Main Streamlit application
├── utils.py         # Utility functions for AI processing
├── config.py        # Configuration and environment variables
├── styles.css       # Custom CSS styles
├── requirements.txt # Project dependencies
└── README.md       # Project documentation
```

## 🌐 Deployment

### Deploy to GitHub:

1. Create a new repository on GitHub
2. Initialize git and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/image-to-post-generator.git
git push -u origin main
```

### Deploy to Streamlit Cloud:

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repository
3. Deploy the app with these settings:
   - Main file path: `main.py`
   - Python version: 3.8+
   - Add your environment variables in Streamlit Cloud settings

## 🔑 Environment Variables

Make sure to set these environment variables:
- `GROQ_API_KEY`: Your Groq API key for AI processing

## 📝 Usage

1. Open the app in your browser
2. Upload an image using the file uploader
3. Click "Generate Content & Hashtags"
4. Wait for the AI to analyze your image
5. Get your generated content and hashtags
6. Copy and use on your social media!

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Groq](https://groq.com/) for the AI processing capabilities
- [Pillow](https://python-pillow.org/) for image processing

## 📧 Contact

Your Name - [your@email.com](mailto:your@email.com)

Project Link: [https://github.com/yourusername/image-to-post-generator](https://github.com/yourusername/image-to-post-generator) # image-to-post-generator
