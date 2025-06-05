import streamlit as st
import os
from utils import (
    analyze_image_and_generate_content,
)
import base64
from io import BytesIO
from PIL import Image
import toml

# Page config
st.set_page_config(
    page_title="Image to Post Generator",
    page_icon="🎨",
    layout="centered"
)

# Load CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# App header
st.markdown("<h1>🎨 Image to Post Generator</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size: 1.2rem; color: var(--text-primary); margin-bottom: 2rem;'>
    Upload an image and get engaging social media content!
</p>
""", unsafe_allow_html=True)

# Load secrets from the secrets.toml file
# Load the API key from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_container_width=True)
    
    # Add a generate button
    if st.button("Generate Content & Hashtags"):
    # Convert image to base64
        buffered = BytesIO()
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            # Create a white background image
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            # Composite the image onto the background
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(buffered, format="JPEG", quality=95)
        image_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Show progress
        progress_bar = st.progress(0)
        
        with st.spinner("🎨 Creating your perfect post..."):
            progress_bar.progress(30)
            
            # Generate content and hashtags
            result = analyze_image_and_generate_content(image_base64, "Instagram")
            
            progress_bar.progress(60)
            
            with st.spinner("🏷️ Adding trending hashtags..."):
                progress_bar.progress(100)
                
                # Display results
                st.success("✨ Your post is ready!")
                
                # Display content
                st.markdown("### 📝 Content")
                st.write(result["content"])
                
                # Display hashtags
                st.markdown("### 🏷️ Hashtags")
                hashtags = " ".join([f"#{tag}" for tag in result["hashtags"]])
                st.write(hashtags)