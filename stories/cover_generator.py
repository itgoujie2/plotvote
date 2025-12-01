"""
Cover image generation using OpenAI DALL-E 3
"""
from openai import OpenAI
from django.conf import settings
import requests
from django.core.files.base import ContentFile
import logging
import re

logger = logging.getLogger(__name__)


def sanitize_prompt_text(text):
    """
    Sanitize text to reduce false positives from OpenAI's content policy

    Removes or replaces words that might trigger the safety filter
    while preserving the meaning for cover generation
    """
    if not text:
        return text

    # Common words that might trigger filters but are fine for book covers
    # Replace with safer alternatives
    replacements = {
        # Violence-related (common in fiction)
        r'\bkill(ed|ing|s)?\b': 'defeat',
        r'\bmurder(ed|ing|s)?\b': 'mystery',
        r'\bdeath\b': 'fate',
        r'\bdie(d|s)?\b': 'fall',
        r'\bblood(y)?\b': 'crimson',
        r'\bweapon(s)?\b': 'artifact',
        r'\bsword(s)?\b': 'blade',
        r'\bgun(s)?\b': 'device',

        # Horror-related
        r'\bhorror\b': 'dark mystery',
        r'\bterror\b': 'suspense',
        r'\bscary\b': 'mysterious',
        r'\bcorpse(s)?\b': 'remains',

        # Mature themes (replace carefully)
        r'\bsexy?\b': 'attractive',
        r'\bnaked\b': 'unadorned',
    }

    sanitized = text
    for pattern, replacement in replacements.items():
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def build_cover_prompt(title, description, genre, characters='', world_building='', themes='', sanitize=True):
    """
    Build an optimized prompt for DALL-E 3 based on story details

    Args:
        title: Story title
        description: Story description/premise
        genre: Story genre
        characters: Optional character descriptions
        world_building: Optional world/setting details
        themes: Optional themes and tone
        sanitize: Whether to sanitize content for safety filters
    """
    # Sanitize inputs if requested
    if sanitize:
        title = sanitize_prompt_text(title)
        description = sanitize_prompt_text(description)
        characters = sanitize_prompt_text(characters)
        world_building = sanitize_prompt_text(world_building)
        themes = sanitize_prompt_text(themes)

    # Genre-specific style guidance (safer descriptions)
    genre_styles = {
        'fantasy': 'epic fantasy illustration, magical atmosphere, dramatic lighting, mystical',
        'scifi': 'futuristic sci-fi art, sleek technology, space aesthetic, advanced',
        'romance': 'romantic cover art, soft lighting, dreamy atmosphere, elegant',
        'mystery': 'mystery cover, atmospheric, noir style, intriguing',
        'thriller': 'suspenseful cover art, dramatic lighting, intense atmosphere',
        'horror': 'dark mystery cover, eerie atmosphere, mysterious',
        'adventure': 'adventure book cover, dynamic scene, exciting, epic',
        'literary': 'literary fiction cover, artistic, sophisticated, thoughtful composition',
        'other': 'professional book cover art, artistic, engaging',
    }

    style = genre_styles.get(genre, genre_styles['other'])

    # Build comprehensive prompt using all available information
    prompt_parts = [f'Professional book cover art for "{title}".']

    # Add story premise (main description)
    if description:
        prompt_parts.append(f"Story: {description[:200]}")

    # Extract key visual elements from characters (first 150 chars)
    if characters:
        # Extract main character info for visual representation
        char_snippet = characters[:150].strip()
        if char_snippet:
            prompt_parts.append(f"Main character: {char_snippet}")

    # Extract key visual elements from world building (first 150 chars)
    if world_building:
        world_snippet = world_building[:150].strip()
        if world_snippet:
            prompt_parts.append(f"Setting: {world_snippet}")

    # Extract mood/atmosphere from themes (first 100 chars)
    if themes:
        theme_snippet = themes[:100].strip()
        if theme_snippet:
            prompt_parts.append(f"Mood: {theme_snippet}")

    # Combine all parts
    content = " ".join(prompt_parts)

    # Build final prompt with style guidance
    prompt = f"""{content}
Style: {style}, trending on artstation, high quality digital art, professional cover design, dramatic composition, eye-catching.
Important: No text, no words, no title, no author name on the cover."""

    return prompt


def build_simple_cover_prompt(title, genre):
    """
    Build a simplified, safer prompt for retry after content policy violation

    Uses only title and genre with minimal description
    """
    # Sanitize title
    title = sanitize_prompt_text(title)

    # Safe genre descriptions
    safe_genre_prompts = {
        'fantasy': 'A beautiful fantasy book cover with magical elements and mystical atmosphere',
        'scifi': 'A futuristic science fiction book cover with advanced technology and space aesthetic',
        'romance': 'An elegant romantic book cover with soft lighting and dreamy atmosphere',
        'mystery': 'An intriguing mystery book cover with atmospheric noir style',
        'thriller': 'A suspenseful book cover with dramatic lighting and intense atmosphere',
        'horror': 'A mysterious dark book cover with eerie atmosphere',
        'adventure': 'An exciting adventure book cover with dynamic composition',
        'literary': 'An artistic literary fiction cover with sophisticated design',
        'other': 'A professional book cover with artistic design',
    }

    base_prompt = safe_genre_prompts.get(genre, safe_genre_prompts['other'])

    prompt = f"""{base_prompt} for a book titled "{title}".
Professional cover design, trending on artstation, high quality digital art, dramatic composition.
Important: No text, no words, no title on the cover."""

    return prompt


def generate_story_cover(title, description, genre, characters='', world_building='', themes='',
                         size="1024x1024", quality="standard"):
    """
    Generate a cover image for a story using DALL-E 3

    Automatically retries with simplified prompt if content policy violation occurs

    Args:
        title: Story title
        description: Story description
        genre: Story genre
        characters: Optional character descriptions
        world_building: Optional world/setting details
        themes: Optional themes and tone
        size: Image size ("1024x1024", "1792x1024", "1024x1792")
        quality: Image quality ("standard" or "hd")

    Returns:
        tuple: (success: bool, result: image_url or error_message)
    """
    # Check if API key is configured
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.error("OPENAI_API_KEY not configured in settings")
        return False, "OpenAI API key not configured. Please contact support."

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Try with full detailed prompt first
    try:
        # Build the prompt with all available story details (with sanitization)
        prompt = build_cover_prompt(title, description, genre, characters, world_building, themes, sanitize=True)
        logger.info(f"Generating cover with detailed prompt: {prompt[:150]}...")

        # Generate image
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )

        # Get the image URL
        image_url = response.data[0].url
        logger.info(f"Successfully generated cover image: {image_url}")

        return True, image_url

    except Exception as e:
        error_str = str(e)

        # Check if it's a content policy violation
        if 'content_policy_violation' in error_str or 'safety system' in error_str.lower():
            logger.warning(f"Content policy violation on detailed prompt, retrying with simplified prompt...")

            # Retry with simplified, safer prompt
            try:
                simple_prompt = build_simple_cover_prompt(title, genre)
                logger.info(f"Retrying with simple prompt: {simple_prompt[:100]}...")

                response = client.images.generate(
                    model="dall-e-3",
                    prompt=simple_prompt,
                    size=size,
                    quality=quality,
                    n=1,
                )

                image_url = response.data[0].url
                logger.info(f"Successfully generated cover with simplified prompt: {image_url}")

                return True, image_url

            except Exception as retry_error:
                logger.error(f"Error on retry with simplified prompt: {str(retry_error)}")
                return False, "Unable to generate cover. The story content may contain themes that are difficult to visualize. Try simplifying your description."

        else:
            # Other error (API key, network, etc.)
            logger.error(f"Error generating cover image: {error_str}")
            return False, f"Failed to generate cover: {error_str}"


def download_and_save_cover(story, image_url):
    """
    Download cover image from URL and save to story model

    Args:
        story: Story model instance
        image_url: URL of the generated image

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Download the image
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            return False, f"Failed to download image: HTTP {response.status_code}"

        # Save to story model
        filename = f"{story.slug}_cover.png"
        story.cover_image.save(
            filename,
            ContentFile(response.content),
            save=True
        )

        logger.info(f"Successfully saved cover image for story: {story.slug}")
        return True, "Cover image saved successfully"

    except requests.exceptions.Timeout:
        logger.error("Timeout downloading cover image")
        return False, "Timeout downloading image. Please try again."
    except Exception as e:
        logger.error(f"Error saving cover image: {str(e)}")
        return False, f"Failed to save image: {str(e)}"


def generate_and_save_cover(story, size="1024x1024", quality="standard"):
    """
    Generate and save cover image for a story (convenience function)

    Args:
        story: Story model instance
        size: Image size
        quality: Image quality

    Returns:
        tuple: (success: bool, message: str, image_url: str or None)
    """
    # Generate the cover
    success, result = generate_story_cover(
        story.title,
        story.description,
        story.genre,
        size=size,
        quality=quality
    )

    if not success:
        return False, result, None

    image_url = result

    # Download and save
    success, message = download_and_save_cover(story, image_url)

    if success:
        return True, "Cover image generated and saved successfully!", image_url
    else:
        # Return the URL even if saving failed, so user can see it
        return False, message, image_url
