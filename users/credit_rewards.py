"""
Credit reward utilities for PlotVote
Handles reading rewards, milestone tracking, and credit awards
"""
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.db import models
from .models import ChapterView, CreditTransaction


# Reading reward milestones
READING_MILESTONES = [
    {'readers': 10, 'credits': 1},
    {'readers': 50, 'credits': 5},
    {'readers': 100, 'credits': 12},
    {'readers': 500, 'credits': 75},
    {'readers': 1000, 'credits': 200},
]


def check_reading_rewards(story):
    """
    Check if a story has reached any reading milestones and award credits

    Args:
        story: Story object to check

    Returns:
        dict: {'awarded': bool, 'milestone': int, 'credits': int} or None
    """
    if not story.created_by:
        return None

    # Only count qualified reads (60%+ completion, unique readers)
    unique_qualified_readers = ChapterView.objects.filter(
        chapter__story=story,
        read_percentage__gte=60
    ).values('reader').distinct().count()

    # Check each milestone
    for milestone in READING_MILESTONES:
        if unique_qualified_readers >= milestone['readers']:
            # Check if this milestone was already awarded
            already_awarded = CreditTransaction.objects.filter(
                user=story.created_by,
                transaction_type='earned',
                description__contains=f"Reading reward: {milestone['readers']} readers",
                story=story
            ).exists()

            if not already_awarded:
                # Check monthly cap (50 credits max from reading rewards)
                current_month_reading_credits = CreditTransaction.objects.filter(
                    user=story.created_by,
                    transaction_type='earned',
                    description__contains='Reading reward',
                    created_at__year=timezone.now().year,
                    created_at__month=timezone.now().month
                ).aggregate(models.Sum('amount'))['amount__sum'] or 0

                # Award credits if under monthly cap
                credits_to_award = milestone['credits']
                if current_month_reading_credits + credits_to_award <= 50:
                    profile = story.created_by.profile
                    profile.add_credits(credits_to_award, source='earned')

                    CreditTransaction.objects.create(
                        user=story.created_by,
                        amount=credits_to_award,
                        transaction_type='earned',
                        description=f'Reading reward: {milestone["readers"]} readers on "{story.title}"',
                        story=story,
                        balance_after=profile.credits
                    )

                    return {
                        'awarded': True,
                        'milestone': milestone['readers'],
                        'credits': credits_to_award
                    }

    return None


def record_chapter_view(chapter, reader, read_percentage=100, time_spent=0):
    """
    Record or update a chapter view

    Args:
        chapter: Chapter object
        reader: User who read the chapter
        read_percentage: Percentage of chapter read (0-100)
        time_spent: Time spent reading in seconds

    Returns:
        ChapterView object
    """
    view, created = ChapterView.objects.update_or_create(
        chapter=chapter,
        reader=reader,
        defaults={
            'read_percentage': max(read_percentage, 0, 100),
            'time_spent_seconds': time_spent
        }
    )

    # Check if this triggered a reading reward milestone
    if view.is_qualified_read:
        reward = check_reading_rewards(chapter.story)
        if reward and reward['awarded']:
            return view, reward

    return view, None


def get_story_reader_count(story):
    """
    Get the number of unique qualified readers for a story

    Args:
        story: Story object

    Returns:
        int: Number of unique readers who read 60%+ of at least one chapter
    """
    return ChapterView.objects.filter(
        chapter__story=story,
        read_percentage__gte=60
    ).values('reader').distinct().count()


def get_user_reading_credits_this_month(user):
    """
    Get total reading reward credits earned by user this month

    Args:
        user: User object

    Returns:
        int: Total credits earned from reading rewards this month
    """
    from django.db import models

    return CreditTransaction.objects.filter(
        user=user,
        transaction_type='earned',
        description__contains='Reading reward',
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).aggregate(total=models.Sum('amount'))['total'] or 0
