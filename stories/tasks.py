"""
Celery tasks for stories app
"""
from celery import shared_task
from django.utils import timezone
from .models import Story, Chapter, Prompt
from .ai_service import ChapterGenerator


@shared_task
def generate_chapter_from_prompt(prompt_id):
    """
    Generate a chapter from a winning prompt using AI
    """
    try:
        prompt = Prompt.objects.get(id=prompt_id)
        story = prompt.story

        # Double-check prompt is a winner
        if prompt.status != 'winner':
            return f"Prompt {prompt_id} is not a winner (status: {prompt.status})"

        # Check if chapter already exists
        existing_chapter = Chapter.objects.filter(
            story=story,
            chapter_number=prompt.chapter_number
        ).first()

        if existing_chapter:
            return f"Chapter {prompt.chapter_number} already exists for story {story.title}"

        # Generate chapter using AI
        generator = ChapterGenerator()
        chapter_data = generator.generate_chapter(
            story=story,
            prompt_text=prompt.prompt_text,
            chapter_number=prompt.chapter_number
        )

        # Create chapter
        chapter = Chapter.objects.create(
            story=story,
            chapter_number=prompt.chapter_number,
            title=chapter_data['title'],
            content=chapter_data['content'],
            prompt_used=prompt,
            word_count=chapter_data['word_count'],
            read_time_minutes=chapter_data['read_time_minutes'],
            status='published',
            published_at=timezone.now()
        )

        return f"Successfully generated chapter {chapter.chapter_number} for {story.title}"

    except Prompt.DoesNotExist:
        return f"Prompt {prompt_id} not found"
    except Exception as e:
        return f"Error generating chapter: {str(e)}"
