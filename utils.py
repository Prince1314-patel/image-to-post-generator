import httpx
import json
import os
import logging
import base64
from io import BytesIO
from PIL import Image
from groq import Groq
from functools import lru_cache
from config import GROQ_API_KEY, OPENROUTER_API_KEY
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelManager:
    _instance = None
    _groq_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModelManager, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self):
        """Initialize AI models with proper device selection and optimization"""
        try:
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
    prompt = f"""You are a social media expert. Generate 5 relevant and trending hashtags for this {platform} post:\n\n{post}\n\nYour response must be a valid JSON array of hashtags without the # symbol. Example:\n[\"marketing\", \"business\", \"success\"]\n\nIMPORTANT: \n- Respond ONLY with the JSON array\n- Maximum 5 hashtags\n- Don't include the # symbol\n- Make them relevant and trending\n- For {platform} specifically"""

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
    Generate a detailed caption for an image using OpenRouter's Llama 3.2 Vision model.
    Args:
        image_base64 (str): Base64 encoded image
    Returns:
        str: Detailed caption describing the image
    """
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "max_tokens": 128
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        caption = result["choices"][0]["message"]["content"].strip()
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
    prompt = f"""You are a {platform} expert. Create a medium-length caption based on this image description:\n\n{caption}\n\nRequirements:\n1. Write 3-4 lines of engaging content\n2. Include a hook or question to encourage engagement\n3. Add 2-3 relevant emojis spread throughout\n4. Tell a mini-story or share a relatable moment\n5. Keep it personal and authentic\n6. Avoid hashtags in the main content\n\nExample format:\n"✨ Golden hour magic hitting different today! Taking in this stunning mountain view while sipping my morning coffee ☕️\n\nSometimes the best moments are these simple ones. Who else loves starting their day with views like this? 🏔️"\n\nMake it engaging but not overly verbose!"""

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