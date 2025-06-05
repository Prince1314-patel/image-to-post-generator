import httpx
import json
import os
from groq import Groq
from config import GROQ_API_KEY

# Initialize Groq client with custom httpx client
http_client = httpx.Client(
    base_url="https://api.groq.com/v1",
    timeout=60.0
)

client = Groq(
    api_key=GROQ_API_KEY,
)

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
        response = client.chat.completions.create(
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
        return ["socialmedia", "post", "trending", "viral", "content"]

def generate_image_caption(image_base64: str) -> str:
    """
    Generate a detailed caption for an image using Groq's vision model.
    
    Args:
        image_base64 (str): Base64 encoded image
    
    Returns:
        str: Detailed caption describing the image
    """
    try:
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this image in detail and describe:
1. Main subjects/objects
2. Actions/activities
3. Setting/environment
4. Colors and visual elements
5. Mood/atmosphere

Be specific and descriptive but concise. Your description should be 2-3 sentences long."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }],
            model="mistral-saba-24b",
            temperature=0.7,
            max_tokens=200,
        )
        
        caption = response.choices[0].message.content.strip()
        return caption
        
    except Exception as e:
        print(f"Error in generate_image_caption: {str(e)}")  # Add debug print
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
        response = client.chat.completions.create(
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
            "hashtags": hashtags
        }
        
    except Exception as e:
        return {
            "content": "This image looks amazing! Perfect for sharing on social media. What do you think?",
            "hashtags": ["photooftheday", "instagood", "picoftheday", "beautiful", "photography"]
        }