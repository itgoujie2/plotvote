"""
Management command to check Celery task status for chapter generation
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from stories.models import Prompt, Chapter
from celery.result import AsyncResult
from plotvote.celery import app
import redis


class Command(BaseCommand):
    help = 'Check Celery task status and verify chapter generation for winning prompts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prompt-id',
            type=int,
            help='Check specific prompt ID',
            default=None
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='Show all winning prompts (not just recent)',
        )

    def handle(self, *args, **options):
        prompt_id = options['prompt_id']
        show_all = options['show_all']

        self.stdout.write(self.style.SUCCESS('\n=== Celery Task Status Checker ===\n'))

        # Check Redis connection
        try:
            redis_client = redis.Redis.from_url('redis://localhost:6379/0')
            redis_client.ping()
            self.stdout.write(self.style.SUCCESS('✓ Redis connection: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Redis connection: FAILED - {e}'))
            self.stdout.write(self.style.WARNING('\nMake sure Redis is running: redis-server'))
            return

        # Check Celery worker
        try:
            inspector = app.control.inspect()
            active_workers = inspector.active()
            if active_workers:
                self.stdout.write(self.style.SUCCESS(f'✓ Celery workers: {len(active_workers)} active'))
                for worker_name in active_workers.keys():
                    self.stdout.write(f'  - {worker_name}')
            else:
                self.stdout.write(self.style.ERROR('✗ Celery workers: No active workers found'))
                self.stdout.write(self.style.WARNING('\nStart Celery worker: celery -A plotvote worker --loglevel=info'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Celery worker check failed: {e}'))

        self.stdout.write('')

        # Check winning prompts
        if prompt_id:
            prompts = Prompt.objects.filter(id=prompt_id)
        elif show_all:
            prompts = Prompt.objects.filter(status='winner').order_by('-created_at')
        else:
            # Show recent winning prompts (last 24 hours)
            recent_time = timezone.now() - timezone.timedelta(hours=24)
            prompts = Prompt.objects.filter(
                status='winner',
                created_at__gte=recent_time
            ).order_by('-created_at')

        if not prompts.exists():
            self.stdout.write(self.style.WARNING('No winning prompts found'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {prompts.count()} winning prompt(s):\n'))

        for prompt in prompts:
            self.stdout.write(f'Prompt ID: {prompt.id}')
            self.stdout.write(f'Story: {prompt.story.title}')
            self.stdout.write(f'Chapter: {prompt.chapter_number}')
            self.stdout.write(f'Status: {prompt.status}')
            self.stdout.write(f'Created: {prompt.created_at}')
            self.stdout.write(f'Prompt: {prompt.prompt_text[:80]}...')

            # Check if chapter was generated
            chapter = Chapter.objects.filter(
                story=prompt.story,
                chapter_number=prompt.chapter_number,
                prompt_used=prompt
            ).first()

            if chapter:
                self.stdout.write(self.style.SUCCESS(f'✓ Chapter generated: "{chapter.title}"'))
                self.stdout.write(f'  Status: {chapter.status}')
                self.stdout.write(f'  Words: {chapter.word_count}')
                self.stdout.write(f'  Published: {chapter.published_at}')
            else:
                self.stdout.write(self.style.ERROR('✗ Chapter NOT generated yet'))

                # Try to check if there's any chapter for this chapter number
                existing_chapter = Chapter.objects.filter(
                    story=prompt.story,
                    chapter_number=prompt.chapter_number
                ).first()

                if existing_chapter:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ A chapter already exists for chapter {prompt.chapter_number}'
                    ))
                    self.stdout.write(f'    Used prompt: {existing_chapter.prompt_used_id}')
                else:
                    self.stdout.write(self.style.WARNING(
                        '  Task may still be running or failed. Check Celery logs.'
                    ))

            self.stdout.write('-' * 60)
            self.stdout.write('')

        # Show active tasks
        try:
            inspector = app.control.inspect()
            active_tasks = inspector.active()

            if active_tasks:
                task_count = sum(len(tasks) for tasks in active_tasks.values())
                if task_count > 0:
                    self.stdout.write(self.style.SUCCESS(f'\nActive tasks: {task_count}'))
                    for worker, tasks in active_tasks.items():
                        for task in tasks:
                            self.stdout.write(f'  Worker: {worker}')
                            self.stdout.write(f'  Task: {task["name"]}')
                            self.stdout.write(f'  Args: {task.get("args", [])}')
                            self.stdout.write('')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not check active tasks: {e}'))

        # Helpful tips
        self.stdout.write(self.style.SUCCESS('\n=== Helpful Commands ==='))
        self.stdout.write('Check Celery worker logs: celery -A plotvote worker --loglevel=info')
        self.stdout.write('Monitor Celery tasks: celery -A plotvote events')
        self.stdout.write('Check this script with specific prompt: python manage.py check_celery_tasks --prompt-id <ID>')
        self.stdout.write('View all winning prompts: python manage.py check_celery_tasks --show-all')
        self.stdout.write('')
