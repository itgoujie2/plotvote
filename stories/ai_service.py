"""
AI Service for generating story chapters using OpenAI
"""
import logging
from openai import OpenAI
from django.conf import settings
from .models import Story, Chapter, count_words, calculate_read_time

logger = logging.getLogger(__name__)


class ChapterGenerator:
    """Generate story chapters using OpenAI GPT"""

    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Fast and cheap for MVP

    def generate_chapter(self, story, prompt_text, chapter_number):
        """
        Generate a chapter from a winning prompt

        Args:
            story: Story instance
            prompt_text: The winning prompt text
            chapter_number: Chapter number to generate

        Returns:
            dict: {'title': str, 'content': str, 'word_count': int}
        """
        try:
            # Build context from previous chapters
            context = self._build_context(story, chapter_number)

            # Create system prompt
            system_prompt = self._create_system_prompt(story, context)

            # Create user prompt
            user_prompt = f"""Write Chapter {chapter_number} based on this direction:

"{prompt_text}"

Requirements:
- Write 1500-2500 words
- Maintain consistent tone and style from previous chapters
- Develop characters naturally
- Include vivid descriptions and dialogue
- End with a hook that makes readers want the next chapter
- Do NOT include "Chapter X" in your response - just write the content
"""

            logger.info(f"Generating chapter {chapter_number} for story: {story.title}")

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3500,
                temperature=0.8,  # Creative but not too random
            )

            content = response.choices[0].message.content.strip()
            word_count = count_words(content)

            logger.info(f"Generated {word_count} words for chapter {chapter_number}")

            # Generate chapter title
            title = self._generate_title(story, chapter_number, content)

            # Calculate read time
            read_time_minutes = calculate_read_time(word_count)

            return {
                'title': title,
                'content': content,
                'word_count': word_count,
                'read_time_minutes': read_time_minutes
            }

        except Exception as e:
            logger.error(f"Error generating chapter: {e}", exc_info=True)
            raise

    def _build_context(self, story, chapter_number):
        """Build context summary from previous chapters"""
        if chapter_number == 1:
            return f"This is the first chapter. Story premise: {story.description}"

        # Get previous chapters
        previous_chapters = Chapter.objects.filter(
            story=story,
            chapter_number__lt=chapter_number,
            status='published'
        ).order_by('chapter_number')

        if not previous_chapters.exists():
            return f"Story premise: {story.description}"

        # Summarize previous chapters (keep it concise to save tokens)
        summaries = []
        for ch in previous_chapters:
            # Take first 200 words of each chapter as summary
            summary = ' '.join(ch.content.split()[:200])
            summaries.append(f"Chapter {ch.chapter_number} ({ch.title}): {summary}...")

        context = f"""Story premise: {story.description}

Previous chapters summary:
{chr(10).join(summaries)}"""

        return context

    def _create_system_prompt(self, story, context):
        """Create system prompt for the AI"""
        # Include story framework for consistency
        framework_context = story.get_story_framework_context()

        return f"""You are a creative fiction writer specializing in {story.get_genre_display()} stories.

{"=" * 70}
STORY FRAMEWORK (maintain consistency with these details)
{"=" * 70}

{framework_context}

{"=" * 70}
PREVIOUS CHAPTERS CONTEXT
{"=" * 70}

{context}

CRITICAL GUIDELINES:
- **MAINTAIN STRICT CONSISTENCY** with the Story Framework provided (characters, plot outline, world rules)
- Reference characters by their established names and traits
- Follow the story outline and planned story arc
- Respect the world building rules (magic system, technology, setting, etc.)
- Match the themes and tone specified in the framework
- If character details are provided, use them exactly as described

Your task is to continue this story in a way that:
1. Maintains consistency with established characters and plot
2. Matches the genre conventions ({story.get_genre_display()})
3. Creates engaging, descriptive prose
4. Advances the plot while developing characters
5. Keeps readers wanting more

Write in a clear, engaging style appropriate for the genre. Focus on showing rather than telling."""

    def _generate_title(self, story, chapter_number, content):
        """Generate an engaging title for the chapter"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative writer. Generate a short, engaging chapter title (2-6 words) that captures the essence of the chapter content."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a title for this chapter content (first 500 words):\n\n{' '.join(content.split()[:500])}"
                    }
                ],
                max_tokens=20,
                temperature=0.7,
            )

            title = response.choices[0].message.content.strip().strip('"').strip("'")

            # Fallback if title is too long
            if len(title) > 100:
                title = f"Chapter {chapter_number}"

            return title

        except Exception as e:
            logger.warning(f"Error generating title: {e}")
            return f"Chapter {chapter_number}"


def generate_chapter_from_prompt(prompt):
    """
    Convenience function to generate chapter from a prompt

    Args:
        prompt: Prompt instance (winning prompt)

    Returns:
        Chapter instance (saved to database)
    """
    generator = ChapterGenerator()

    # Generate chapter content
    result = generator.generate_chapter(
        story=prompt.story,
        prompt_text=prompt.prompt_text,
        chapter_number=prompt.chapter_number
    )

    # Create and save chapter
    chapter = Chapter.objects.create(
        story=prompt.story,
        chapter_number=prompt.chapter_number,
        title=result['title'],
        content=result['content'],
        prompt_used=prompt,
        status='published'
    )

    # Update prompt status
    prompt.status = 'winner'
    prompt.save()

    logger.info(f"Chapter {chapter.chapter_number} created: {chapter.title}")

    return chapter
