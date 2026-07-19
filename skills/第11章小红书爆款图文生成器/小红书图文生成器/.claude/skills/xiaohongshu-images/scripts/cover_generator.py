#!/usr/bin/env python3
"""
Cover Image Generator for Xiaohongshu Images Skill

Generates cover images using multiple API providers:
  - volcano (recommended): doubao-seedream via 火山方舟 API
  - yunwu: Gemini image generation via yunwu.ai
  - openai: DALL-E via OpenAI API

Usage:
    python cover_generator.py --prompt "Your prompt" --output /path/to/cover.png
    python cover_generator.py --title "Article Title" --api volcano --output /path/to/cover.png

Environment:
    ARK_API_KEY:    API key for 火山方舟 (volcano provider)
    YUNWU_API_KEY:  API key for yunwu.ai (yunwu provider)
    OPENAI_API_KEY: API key for OpenAI (openai provider)
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed.")
    print("Install it with: pip install requests")
    sys.exit(1)


# API Configurations
API_CONFIGS = {
    "volcano": {
        "url": "https://ark.cn-beijing.volces.com/api/v3/images/generations",
        "model": "doubao-seedream-5-0-260128",
        "env_key": "ARK_API_KEY",
        "name": "火山方舟 (Volcano Ark)",
    },
    "yunwu": {
        "url": "https://yunwu.ai/v1/chat/completions",
        "model": "gemini-3-pro-image-preview",
        "env_key": "YUNWU_API_KEY",
        "name": "云雾 API (Yunwu)",
    },
    "openai": {
        "url": "https://api.openai.com/v1/images/generations",
        "model": "dall-e-3",
        "env_key": "OPENAI_API_KEY",
        "name": "OpenAI DALL-E",
    },
}


def get_api_key(api_provider: str) -> str:
    """Get API key from environment variable for the specified provider."""
    config = API_CONFIGS.get(api_provider)
    if not config:
        print(f"Error: Unknown API provider: {api_provider}")
        print(f"Supported providers: {', '.join(API_CONFIGS.keys())}")
        sys.exit(1)

    env_key = config["env_key"]
    api_key = os.environ.get(env_key)
    if not api_key:
        print(f"Error: {env_key} environment variable not set.")
        print("")
        print("To set it, run:")
        print(f'  export {env_key}="your-api-key"')
        print("")
        print("Or add it to your shell profile (~/.zshrc or ~/.bashrc)")
        sys.exit(1)
    return api_key


def extract_title_from_article(article_path: str) -> str:
    """Extract title from markdown article."""
    try:
        with open(article_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to find h1 title
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Try to find title in frontmatter
        match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Use first non-empty line
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('---') and not line.startswith('#'):
                return line[:50]

        return "Article Cover"
    except Exception as e:
        print(f"Warning: Could not read article: {e}")
        return "Article Cover"


def generate_cover_prompt(title: str, style: str = "default") -> str:
    """Generate the prompt for cover image generation."""

    base_prompt = f"""Generate a cover illustration for an article titled: "{title}"

Style Requirements:
- The New Yorker editorial cartoon style
- Flat vector illustration with clean lines
- Minimalist composition with generous whitespace (40-50%)
- No text or words on the image
- Aspect ratio: 3:4 vertical (portrait orientation for mobile)

Color Palette:
- Use a harmonious, sophisticated color scheme
- Soft, muted tones preferred
- Good contrast for readability at small sizes

Character Guidelines (if humans are included):
- Use simplified, icon-style figures (not realistic)
- Default to depicting women aged 25-40 if gender not specified
- Appropriate, professional attire

The illustration should visually represent the article's main theme in a clever, metaphorical way."""

    if style == "tech":
        base_prompt += """

Additional style notes:
- Use cool blue tones (#2563EB, #1E3A5A, #06B6D4)
- Include subtle tech elements (code brackets, circuits, screens)
- Modern, digital aesthetic"""

    elif style == "warm":
        base_prompt += """

Additional style notes:
- Use warm tones (orange, golden yellow, terracotta)
- Friendly, approachable feeling
- Soft, inviting atmosphere"""

    elif style == "minimal":
        base_prompt += """

Additional style notes:
- Extremely minimal composition
- Maximum whitespace (60%+)
- Single focal element
- Zen-like simplicity"""

    elif style == "ink-wash":
        base_prompt += """

Additional style notes:
- Chinese calligraphy and ink-wash illustration style (书法水墨风)
- Zen-like simplicity with generous white space (留白)
- Subtle ink-wash brush strokes as background texture
- Color palette: ink black (#1a1a1a), warm gray (#666666), subtle gold accents (#C9A962)"""

    return base_prompt


def generate_image_volcano(prompt: str, api_key: str) -> bytes:
    """Generate image using 火山方舟 (Volcano Ark) API with doubao-seedream model."""
    config = API_CONFIGS["volcano"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": config["model"],
        "prompt": prompt,
        "response_format": "url",
        "size": "1024x1344",
        "stream": False,
        "watermark": False,
    }

    print("Generating cover image...")
    print(f"Provider: {config['name']}")
    print(f"Model: {config['model']}")

    try:
        response = requests.post(config["url"], headers=headers, json=data, timeout=120)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please try again.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                err_detail = e.response.json()
                print(f"Detail: {json.dumps(err_detail, ensure_ascii=False)}")
            except Exception:
                print(f"Response: {e.response.text[:500]}")
        sys.exit(1)

    result = response.json()

    if "error" in result:
        print(f"Error from API: {json.dumps(result['error'], ensure_ascii=False)}")
        sys.exit(1)

    # Extract image URL from response
    try:
        image_url = result["data"][0]["url"]
    except (KeyError, IndexError):
        print("Error: Unexpected response format from volcano API")
        print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")
        sys.exit(1)

    print("Image generated, downloading...")

    # Download the image from URL
    try:
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to download generated image: {e}")
        sys.exit(1)

    print("Image downloaded successfully")
    return img_response.content


def generate_image_yunwu(prompt: str, api_key: str) -> bytes:
    """Generate image using yunwu.ai API (Gemini image generation)."""
    config = API_CONFIGS["yunwu"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": config["model"],
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    print("Generating cover image...")
    print(f"Provider: {config['name']}")
    print(f"Model: {config['model']}")

    try:
        response = requests.post(config["url"], headers=headers, json=data, timeout=120)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please try again.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}")
        sys.exit(1)

    result = response.json()

    if "error" in result:
        print(f"Error from API: {result['error']}")
        sys.exit(1)

    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    if not content:
        print("Error: Empty response from API")
        sys.exit(1)

    # Extract base64 image from markdown format
    match = re.search(r'data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)', content)

    if not match:
        print("Error: No image found in API response")
        print("Response preview:", content[:200])
        sys.exit(1)

    img_format = match.group(1)
    img_data = match.group(2)

    print(f"Image generated successfully (format: {img_format})")

    return base64.b64decode(img_data)


def generate_image_openai(prompt: str, api_key: str) -> bytes:
    """Generate image using OpenAI DALL-E API."""
    config = API_CONFIGS["openai"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": config["model"],
        "prompt": prompt,
        "n": 1,
        "size": "1024x1792",
        "response_format": "b64_json",
    }

    print("Generating cover image...")
    print(f"Provider: {config['name']}")
    print(f"Model: {config['model']}")

    try:
        response = requests.post(config["url"], headers=headers, json=data, timeout=120)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please try again.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}")
        sys.exit(1)

    result = response.json()

    if "error" in result:
        print(f"Error from API: {result['error']}")
        sys.exit(1)

    try:
        img_data = result["data"][0]["b64_json"]
    except (KeyError, IndexError):
        print("Error: Unexpected response format from OpenAI API")
        sys.exit(1)

    print("Image generated successfully")

    return base64.b64decode(img_data)


# Dispatch table for image generation
IMAGE_GENERATORS = {
    "volcano": generate_image_volcano,
    "yunwu": generate_image_yunwu,
    "openai": generate_image_openai,
}


def generate_image(prompt: str, api_key: str, api_provider: str = "volcano") -> bytes:
    """Generate an image using the specified API provider."""
    generator = IMAGE_GENERATORS.get(api_provider)
    if not generator:
        print(f"Error: Unknown API provider: {api_provider}")
        print(f"Supported providers: {', '.join(IMAGE_GENERATORS.keys())}")
        sys.exit(1)
    return generator(prompt, api_key)


def save_image(img_bytes: bytes, output_path: str):
    """Save image bytes to file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "wb") as f:
        f.write(img_bytes)

    print(f"Image saved to: {output}")
    print(f"File size: {len(img_bytes):,} bytes")


def main():
    parser = argparse.ArgumentParser(
        description="Generate cover images for Xiaohongshu articles"
    )
    parser.add_argument(
        "--prompt",
        help="Direct prompt for image generation",
    )
    parser.add_argument(
        "--article",
        help="Path to article file (will extract title for prompt)",
    )
    parser.add_argument(
        "--title",
        help="Article title (used if --article not provided)",
    )
    parser.add_argument(
        "--style",
        choices=["default", "tech", "warm", "minimal", "ink-wash"],
        default="default",
        help="Cover style preset",
    )
    parser.add_argument(
        "--api",
        choices=["volcano", "yunwu", "openai"],
        default="volcano",
        help="API provider to use (default: volcano)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the generated image",
    )

    args = parser.parse_args()

    # Get API key for the chosen provider
    api_key = get_api_key(args.api)

    # Determine prompt
    if args.prompt:
        prompt = args.prompt
    elif args.article:
        title = extract_title_from_article(args.article)
        print(f"Extracted title: {title}")
        prompt = generate_cover_prompt(title, args.style)
    elif args.title:
        prompt = generate_cover_prompt(args.title, args.style)
    else:
        print("Error: Must provide --prompt, --article, or --title")
        sys.exit(1)

    # Generate and save image
    img_bytes = generate_image(prompt, api_key, args.api)
    save_image(img_bytes, args.output)

    print("\nCover generation complete!")


if __name__ == "__main__":
    main()
