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

        # Build context from previous chapters
        context = f"Story Premise:\n"
        context += f"Title: {story.title}\n"
        context += f"Genre: {story.get_genre_display()}\n"
        context += f"Language: {story.get_language_display()}\n"
        context += f"Description: {story.description}\n\n"

        if previous_chapters and previous_chapters.exists():
            context += "Previous Chapters:\n"
            context += "=" * 50 + "\n\n"

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

Guidelines:
- Write in {story.get_language_display()} language
- Maintain consistency with the story's tone and style
- Aim for 800-1500 words
- Create engaging, descriptive prose
- End with a hook that makes readers want to continue

Format your response EXACTLY as follows:
TITLE: [Your chapter title here]
CONTENT:
[Your chapter content here]"""

        user_prompt = f"""{context}

User's prompt for the next chapter: {prompt_text}

Please generate the next chapter with a compelling title and engaging content."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )

        # Parse response
        content = response.choices[0].message.content.strip()

        # Extract title and content
        title = "Untitled Chapter"
        chapter_content = content

        if content.startswith("TITLE:"):
            lines = content.split('\n', 2)
            if len(lines) >= 1:
                title = lines[0].replace("TITLE:", "").strip()
            if len(lines) >= 3 and lines[1].strip().startswith("CONTENT:"):
                chapter_content = lines[2].strip()
            elif len(lines) >= 2:
                # Handle case where CONTENT: is on same line or missing
                rest = '\n'.join(lines[1:])
                chapter_content = rest.replace("CONTENT:", "").strip()

        return {
            'title': title,
            'content': chapter_content
        }

    except Exception as e:
        return {
            'error': f'Error generating chapter: {str(e)}'
        }
