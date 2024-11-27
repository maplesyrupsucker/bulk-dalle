# How to run this script:
# 1. Make sure you have the required libraries installed (openai, python-frontmatter, Pillow, requests)
# 2. Set your OpenAI API key in the script or as an environment variable
# 3. Navigate to the directory containing this script
# 4. Run the script using: python bulk_thumbs.py

import os
import sys
import openai
import xml.etree.ElementTree as ET
import requests
import time
from PIL import Image
from io import BytesIO
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    filename='icon_generation.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constants
SITEMAP_URL = "https://www.bitcoin.com/sitemap-0.xml"
SAVE_STATE_FILE = "generation_state.json"
OUTPUT_DIR = "generated_icons"
EXCLUDED_LANGS = ['/de/', '/es/', '/fr/', '/it/', '/ru/', '/zh/', '/ja/']
REQUIRED_PATH = '/get-started/'

def load_save_state():
    """Load the save state from file if it exists."""
    try:
        with open(SAVE_STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'processed_slugs': [], 'failed_slugs': []}

def save_state(state):
    """Save the current state to file."""
    with open(SAVE_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_clean_slug(url):
    """Extract and clean slug from URL."""
    # Get the part after get-started/
    slug = url.split('/get-started/')[-1].strip('/')
    # Remove hyphens and replace with spaces
    return slug.replace('-', ' ')

def fetch_sitemap_urls():
    """Fetch and parse the sitemap URLs."""
    try:
        response = requests.get(SITEMAP_URL)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # Extract all URLs from sitemap
        urls = []
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            url_text = url.text
            
            # Check if URL contains /get-started/ and doesn't contain excluded languages
            if REQUIRED_PATH in url_text and not any(lang in url_text for lang in EXCLUDED_LANGS):
                urls.append(url_text)
        
        return urls
    except Exception as e:
        logging.error(f"Error fetching sitemap: {str(e)}")
        return []

def generate_icon(slug):
    """Generate an icon using OpenAI's DALL-E."""
    try:
        prompt = f"Create a 3D minimalist icon design featuring vibrant, floating tokens and bitcoin coins,representing digital finance and cryptocurrency. Include a dynamic composition of colorful elements. Subject should relate to '{slug}'. The icon should have a clean, modern style suitable for UI design."
        
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        # Download and process the image
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        # Resize the image to 256x256 after downloading
        image = image.resize((256, 256), Image.Resampling.LANCZOS)
        
        # Create filename from slug
        filename = f"{slug.replace(' ', '_')}_icon.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Save the image
        image.save(filepath, "PNG")
        return True, filepath
    
    except Exception as e:
        logging.error(f"Error generating icon for {slug}: {str(e)}")
        return False, str(e)

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load previous state
    state = load_save_state()
    
    # Fetch URLs from sitemap
    urls = fetch_sitemap_urls()
    logging.info(f"Found {len(urls)} URLs to process")
    
    # Process each URL
    for url in urls:
        slug = get_clean_slug(url)
        
        # Skip if already processed
        if slug in state['processed_slugs']:
            logging.info(f"Skipping {slug} - already processed")
            continue
        
        logging.info(f"Processing: {slug}")
        print(f"Generating icon for: {slug}")
        
        success, result = generate_icon(slug)
        
        if success:
            state['processed_slugs'].append(slug)
            logging.info(f"Successfully generated icon: {result}")
            print(f"Success: {result}")
        else:
            state['failed_slugs'].append({'slug': slug, 'error': result})
            logging.error(f"Failed to generate icon for {slug}: {result}")
            print(f"Failed: {result}")
        
        # Save state after each generation
        save_state(state)
        
        # Rate limiting
        time.sleep(2)
    
    print("Icon generation completed!")
    logging.info("Icon generation completed!")
    
    if state['failed_slugs']:
        print("\nFailed generations:")
        for fail in state['failed_slugs']:
            print(f"- {fail['slug']}: {fail['error']}")

if __name__ == "__main__":
    # Set up OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai.api_key:
        print("Error: OpenAI API key not found in environment variables")
        sys.exit(1)
    
    main()