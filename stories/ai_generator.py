"""
AI chapter generation using OpenAI API
"""
from django.conf import settings
from openai import OpenAI


def generate_chapter(story, prompt_text, previous_chapters=None):
    """
    Generate a chapter using OpenAI GPT-4 based on story context and prompt

    Args:
        story: Story model instance
        prompt_text: User's prompt for what should happen in this chapter
        previous_chapters: QuerySet or list of previous Chapter objects

    Returns:
        dict: {'title': str, 'content': str} or {'error': str}
    """
    if not settings.OPENAI_API_KEY:
        return {
            'error': 'OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.'
        }

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Build context using story framework (story bible)
        context = "=" * 70 + "\n"
        context += "STORY FRAMEWORK (maintain consistency with these details)\n"
        context += "=" * 70 + "\n\n"

        # Include the complete story framework
        context += story.get_story_framework_context()
        context += "\n"

        if previous_chapters and previous_chapters.exists():
            context += "=" * 70 + "\n"
            context += "PREVIOUS CHAPTERS (for continuity)\n"
            context += "=" * 70 + "\n\n"

            # Include up to the last 2 complete chapters for better context
            for chapter in previous_chapters[:2]:
                context += f"Chapter {chapter.chapter_number}: {chapter.title}\n"
                context += "-" * 50 + "\n"
                # Include more content - up to 2000 characters or full chapter
                content_preview = chapter.content[:2000] if len(chapter.content) > 2000 else chapter.content
                context += f"{content_preview}"
                if len(chapter.content) > 2000:
                    context += "...\n"
                context += "\n\n"

        # Create the prompt for GPT-4
        system_prompt = f"""You are a creative fiction writer specializing in {story.get_genre_display()} stories.
Your task is to write the next chapter of an ongoing story based on the context provided and the user's prompt.

CRITICAL GUIDELINES:
- Write in {story.get_language_display()} language
- **MAINTAIN STRICT CONSISTENCY** with the Story Framework provided (characters, plot outline, world rules)
- Reference characters by their established names and traits
- Follow the story outline and planned story arc
- Respect the world building rules (magic system, technology, setting, etc.)
- Match the themes and tone specified in the framework
- Aim for 800-1500 words
- Create engaging, descriptive prose
- End with a hook that makes readers want to continue
- If character details are provided, use them exactly as described

Format your response EXACTLY as follows:
TITLE: [Your chapter title here]
CONTENT:
[Your chapter content here]"""

        user_prompt = f"""{context}

User's prompt for the next chapter: {prompt_text}

Please generate the next chapter with a compelling title and engaging content."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )

        # Parse response
        content = response.choices[0].message.content.strip()

        # Extract title and content - more robust parsing
        title = "Untitled Chapter"
        chapter_content = content

        # Try to find TITLE: marker (case insensitive)
        import re
        title_match = re.search(r'^TITLE:\s*(.+?)$', content, re.MULTILINE | re.IGNORECASE)
        content_match = re.search(r'^CONTENT:\s*\n(.+)', content, re.MULTILINE | re.IGNORECASE | re.DOTALL)

        if title_match:
            title = title_match.group(1).strip()

        if content_match:
            chapter_content = content_match.group(1).strip()
        elif title_match:
            # If we found title but not explicit CONTENT marker, take everything after title
            title_end = title_match.end()
            chapter_content = content[title_end:].strip()
            # Remove "CONTENT:" if it's at the start
            chapter_content = re.sub(r'^CONTENT:\s*\n?', '', chapter_content, flags=re.IGNORECASE)

        # If no markers found, try to extract first line as title
        if title == "Untitled Chapter" and '\n\n' in content:
            lines = content.split('\n\n', 1)
            potential_title = lines[0].strip()
            # If first line is short enough to be a title (less than 100 chars), use it
            if len(potential_title) < 100 and not potential_title.endswith('.'):
                title = potential_title
                chapter_content = lines[1].strip() if len(lines) > 1 else content

        return {
            'title': title,
            'content': chapter_content
        }

    except Exception as e:
        return {
            'error': f'Error generating chapter: {str(e)}'
        }
