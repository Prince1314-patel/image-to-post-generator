import httpx
import json
import os
import base64
import torch
import logging
from io import BytesIO
from PIL import Image
from transformers import pipeline
from groq import Groq
from functools import lru_cache
from config import GROQ_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelManager:
    _instance = None
    _image_to_text = None
    _groq_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModelManager, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self):
        """Initialize AI models with proper device selection and optimization"""
        try:
            # Check for GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")

            # Initialize BLIP model
            self._image_to_text = pipeline(
                "image-to-text",
                model="Salesforce/blip-image-captioning-base",
                device=device
            )

            # Initialize Groq client
            self._groq_client = Groq(
                api_key=GROQ_API_KEY,
                http_client=httpx.Client(
                    base_url="https://api.groq.com/v1",
                    timeout=60.0
                )
            )
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            raise

    @property
    def image_to_text(self):
        return self._image_to_text

    @property
    def groq_client(self):
        return self._groq_client

# Initialize the singleton
ai_manager = AIModelManager()

@lru_cache(maxsize=32)
def _process_image(image_base64: str) -> Image.Image:
    """
    Convert base64 image to PIL Image with caching.
    Handles RGBA images by converting them to RGB.
    
    Args:
        image_base64 (str): Base64 encoded image
        
    Returns:
        Image.Image: Processed PIL Image in RGB mode
    """
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))
    
    # Convert RGBA or other modes to RGB if necessary
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
        
    return image

def generate_hashtags(post: str, platform: str) -> list:
    """
    Generate relevant hashtags from a given post.
    
    Args:
        post (str): The post content to generate hashtags from
        platform (str): Target social media platform
    
    Returns:
        list: List of generated hashtags
    """
    prompt = f"""You are a social media expert. Generate 5 relevant and trending hashtags for this {platform} post:

{post}

Your response must be a valid JSON array of hashtags without the # symbol. Example:
["marketing", "business", "success"]

IMPORTANT: 
- Respond ONLY with the JSON array
- Maximum 5 hashtags
- Don't include the # symbol
- Make them relevant and trending
- For {platform} specifically"""

    try:
        response = ai_manager.groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "You are a social media expert that always responds in valid JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }],
            model="mistral-saba-24b",
            temperature=0.7,
            max_tokens=100,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to find JSON content if there's any extra text
        if not content.startswith('['):
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
        
        hashtags = json.loads(content)
        
        # Ensure it's a list and limit to 5
        if not isinstance(hashtags, list):
            hashtags = [hashtags]
        hashtags = hashtags[:5]
        
        return hashtags
        
    except Exception as e:
        logger.error(f"Error generating hashtags: {str(e)}")
        return ["socialmedia", "post", "trending", "viral", "content"]

def generate_image_caption(image_base64: str) -> str:
    """
    Generate a detailed caption for an image using BLIP image captioning model.
    
    Args:
        image_base64 (str): Base64 encoded image
    
    Returns:
        str: Detailed caption describing the image
    """
    try:
        # Use cached image processing
        image = _process_image(image_base64)
        
        # Generate caption using BLIP
        result = ai_manager.image_to_text(image)
        
        # BLIP returns a list of dictionaries with generated text
        caption = result[0]['generated_text'] if result else ""
        
        # Enhance the caption to be more descriptive
        caption = f"This image shows {caption.lower()}"
        return caption
        
    except Exception as e:
        logger.error(f"Error in generate_image_caption: {str(e)}")
        return "A captivating image that tells a unique story."

def generate_content_from_caption(caption: str, platform: str) -> str:
    """
    Generate medium-length, engaging social media content based on an image caption.
    
    Args:
        caption (str): Image caption to base content on
        platform (str): Target social media platform
    
    Returns:
        str: Generated social media content
    """
    prompt = f"""You are a {platform} expert. Create a medium-length caption based on this image description:

{caption}

Requirements:
1. Write 3-4 lines of engaging content
2. Include a hook or question to encourage engagement
3. Add 2-3 relevant emojis spread throughout
4. Tell a mini-story or share a relatable moment
5. Keep it personal and authentic
6. Avoid hashtags in the main content

Example format:
"✨ Golden hour magic hitting different today! Taking in this stunning mountain view while sipping my morning coffee ☕️

Sometimes the best moments are these simple ones. Who else loves starting their day with views like this? 🏔️"

Make it engaging but not overly verbose!"""

    try:
        response = ai_manager.groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": f"You are a {platform} expert that creates engaging, medium-length captions."
            },
            {
                "role": "user",
                "content": prompt
            }],
            model="mistral-saba-24b",
            temperature=0.7,
            max_tokens=200,  # Increased for medium-length content
        )
        
        content = response.choices[0].message.content.strip()
        return content
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return "✨ Living for moments like these! Nature's beauty never fails to amaze me 🌿 What's your favorite way to connect with the outdoors? 🌅"

def analyze_image_and_generate_content(image_base64: str, platform: str) -> dict:
    """
    Analyze an image and generate Instagram-style content and hashtags.
    
    Args:
        image_base64 (str): Base64 encoded image
        platform (str): Target social media platform
    
    Returns:
        dict: Contains generated content and hashtags
    """
    try:
        # Step 1: Generate image caption
        caption = generate_image_caption(image_base64)
        
        # Step 2: Generate content based on caption
        content = generate_content_from_caption(caption, platform)
        
        # Step 3: Generate hashtags based on content
        hashtags = generate_hashtags(content, platform)
        
        return {
            "content": content,
            "hashtags": hashtags,
            "caption": caption  # Added for debugging/monitoring
        }
        
    except Exception as e:
        logger.error(f"Error in content generation pipeline: {str(e)}")
        return {
            "content": "This image looks amazing! Perfect for sharing on social media. What do you think?",
            "hashtags": ["photooftheday", "instagood", "picoftheday", "beautiful", "photography"],
            "caption": "Error processing image"
        }