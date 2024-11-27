# bulk-dalle

A Python script to bulk generate icons using OpenAI's DALL-E API for a sitemap of URLs.

## Features
- Automatically fetches URLs from a sitemap
- Generates custom icons using DALL-E for each URL
- Resizes images to 256x256px (customizable)
- Saves state to resume interrupted runs
- Excludes specified language paths
- Includes logging
- Rate limiting to avoid API issues

## Requirements
- Python 3.x
- Required libraries: openai, python-frontmatter, Pillow, requests, python-dotenv

## Setup
1. Install required libraries:
```
pip install openai python-frontmatter Pillow requests python-dotenv
```
2. Set your OpenAI API key in the script or as an environment variable.
3. Run the script:
```
python script.py
```     
