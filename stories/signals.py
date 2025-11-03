"""
Django signals for stories app
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Prompt
from .tasks import generate_chapter_from_prompt


@receiver(pre_save, sender=Prompt)
def track_status_change(sender, instance, **kwargs):
    """Track if prompt status is changing to 'winner'"""
    if instance.pk:
        try:
            old_instance = Prompt.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Prompt.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Prompt)
def auto_generate_chapter_on_winner(sender, instance, created, **kwargs):
    """
    Automatically trigger chapter generation when a prompt becomes a winner
    """
    # Check if status changed to 'winner'
    old_status = getattr(instance, '_old_status', None)

    if instance.status == 'winner' and old_status != 'winner':
        # Trigger Celery task to generate chapter
        generate_chapter_from_prompt.delay(instance.id)
