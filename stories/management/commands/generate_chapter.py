"""
Management command to generate a chapter from the winning prompt
"""
from django.core.management.base import BaseCommand
from stories.models import Story, Prompt
from stories.ai_service import generate_chapter_from_prompt


class Command(BaseCommand):
    help = 'Generate a chapter from the winning prompt for a story'

    def add_arguments(self, parser):
        parser.add_argument(
            'story_slug',
            type=str,
            help='Slug of the story'
        )
        parser.add_argument(
            '--chapter',
            type=int,
            help='Chapter number (default: next chapter)',
            default=None
        )
        parser.add_argument(
            '--prompt-id',
            type=int,
            help='Specific prompt ID to use (default: highest voted)',
            default=None
        )

    def handle(self, *args, **options):
        story_slug = options['story_slug']
        chapter_number = options['chapter']
        prompt_id = options['prompt_id']

        # Get story
        try:
            story = Story.objects.get(slug=story_slug)
        except Story.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Story "{story_slug}" not found'))
            return

        # Determine chapter number
        if chapter_number is None:
            chapter_number = story.current_chapter_number

        self.stdout.write(f'Story: {story.title}')
        self.stdout.write(f'Generating Chapter {chapter_number}...\n')

        # Get prompt
        if prompt_id:
            try:
                prompt = Prompt.objects.get(id=prompt_id, story=story)
            except Prompt.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Prompt {prompt_id} not found'))
                return
        else:
            # Get highest voted prompt for this chapter
            prompt = Prompt.objects.filter(
                story=story,
                chapter_number=chapter_number,
                status__in=['active', 'voting']
            ).order_by('-vote_count', 'created_at').first()

            if not prompt:
                self.stdout.write(self.style.ERROR(f'No prompts found for chapter {chapter_number}'))
                return

        self.stdout.write(f'Using prompt by {prompt.user.username} ({prompt.vote_count} votes):')
        self.stdout.write(f'"{prompt.prompt_text}"\n')

        # Generate chapter
        try:
            chapter = generate_chapter_from_prompt(prompt)

            self.stdout.write(self.style.SUCCESS(f'\n✓ Chapter generated successfully!'))
            self.stdout.write(f'Title: {chapter.title}')
            self.stdout.write(f'Words: {chapter.word_count}')
            self.stdout.write(f'Reading time: {chapter.read_time_minutes} minutes')
            self.stdout.write(f'\nView at: /story/{story.slug}/chapter/{chapter.chapter_number}/')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error generating chapter: {e}'))
