"""
Views for PlotVote stories app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import Story, Chapter, Prompt, Vote, Comment, Feedback
from .ai_generator import generate_chapter
from users.models import CreditTransaction


def homepage(request):
    """Homepage showing active stories, completed stories, and pitched stories (collaborative only)"""
    # Get language filter from query params
    language_filter = request.GET.get('language', '')

    # Base querysets - only show collaborative stories on homepage
    active_stories_qs = Story.objects.filter(status='active', story_type='collaborative')
    completed_stories_qs = Story.objects.filter(status='completed', story_type='collaborative')
    pitched_stories_qs = Story.objects.filter(status='pitch', story_type='collaborative')

    # Apply language filter if specified
    if language_filter:
        active_stories_qs = active_stories_qs.filter(language=language_filter)
        completed_stories_qs = completed_stories_qs.filter(language=language_filter)
        pitched_stories_qs = pitched_stories_qs.filter(language=language_filter)

    # Active stories (ready for chapter prompts)
    active_stories = active_stories_qs.annotate(
        subscriber_count_annotated=Count('subscribers')
    ).order_by('-is_featured', '-created_at')

    # Completed stories (finished stories for reading)
    completed_stories = completed_stories_qs.annotate(
        subscriber_count_annotated=Count('subscribers')
    ).order_by('-updated_at')[:6]  # Latest 6 completed stories

    # Pitched stories (community voting)
    pitched_stories = pitched_stories_qs.annotate(
        upvote_count_annotated=Count('upvoters')
    ).order_by('-upvote_count_annotated', '-created_at')[:6]  # Top 6

    context = {
        'active_stories': active_stories,
        'completed_stories': completed_stories,
        'pitched_stories': pitched_stories,
        'language_choices': Story.LANGUAGE_CHOICES,
        'selected_language': language_filter,
    }
    return render(request, 'stories/homepage.html', context)


def story_detail(request, slug):
    """Story detail page showing all chapters and current voting"""
    story = get_object_or_404(Story, slug=slug)
    chapters = story.chapters.filter(status='published').order_by('chapter_number')

    # Get current voting prompts
    current_prompts = story.prompts.filter(
        status__in=['active', 'voting'],
        chapter_number=story.current_chapter_number
    ).order_by('-vote_count', 'created_at')

    # Check if user has voted
    user_voted_prompt = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(
            user=request.user,
            prompt__in=current_prompts
        ).first()
        if user_vote:
            user_voted_prompt = user_vote.prompt

    context = {
        'story': story,
        'chapters': chapters,
        'current_prompts': current_prompts,
        'user_voted_prompt': user_voted_prompt,
        'is_subscribed': request.user.is_authenticated and story.subscribers.filter(id=request.user.id).exists(),
    }
    return render(request, 'stories/story_detail.html', context)


def chapter_detail(request, slug, chapter_number):
    """Individual chapter reading view"""
    story = get_object_or_404(Story, slug=slug)
    chapter = get_object_or_404(Chapter, story=story, chapter_number=chapter_number, status='published')

    # Record chapter view for logged-in users (assume 100% read for now)
    reward_info = None
    if request.user.is_authenticated and request.user != story.created_by:
        from users.credit_rewards import record_chapter_view
        view, reward = record_chapter_view(chapter, request.user, read_percentage=100)
        reward_info = reward

    # Show reward notification if earned
    if reward_info and reward_info['awarded']:
        messages.success(request, f'🎉 "{story.title}" reached {reward_info["milestone"]} readers! You earned {reward_info["credits"]} credits!')

    # Track ad impression for non-subscribers
    if request.user.is_authenticated:
        if not request.user.profile.has_active_subscription():
            # Record ad view
            from users.models import AdView
            AdView.objects.create(
                user=request.user,
                chapter=chapter,
                ad_duration_seconds=0,  # Banner ads don't have duration
                watched_full=True,  # Banner ads are always "watched"
                skipped_with_credits=False,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
            )

    # Get previous and next chapters
    prev_chapter = Chapter.objects.filter(
        story=story,
        chapter_number=chapter_number - 1,
        status='published'
    ).first()

    next_chapter = Chapter.objects.filter(
        story=story,
        chapter_number=chapter_number + 1,
        status='published'
    ).first()

    comments = chapter.comments.select_related('user').order_by('created_at')

    context = {
        'story': story,
        'chapter': chapter,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'comments': comments,
    }
    return render(request, 'stories/chapter_detail.html', context)


@login_required
def submit_prompt(request, slug):
    """Submit a prompt for next chapter"""
    story = get_object_or_404(Story, slug=slug, status='active')
    next_chapter_number = story.current_chapter_number

    # Check if user already submitted prompt for this chapter
    existing_prompt = Prompt.objects.filter(
        story=story,
        user=request.user,
        chapter_number=next_chapter_number
    ).first()

    if request.method == 'POST':
        prompt_text = request.POST.get('prompt_text', '').strip()

        if not prompt_text:
            messages.error(request, 'Prompt cannot be empty.')
        elif len(prompt_text) > 3000:
            messages.error(request, 'Prompt must be 3000 characters or less.')
        elif existing_prompt:
            messages.error(request, 'You already submitted a prompt for this chapter.')
        else:
            # Create voting deadline (7 days from now)
            voting_ends = timezone.now() + timezone.timedelta(days=7)

            Prompt.objects.create(
                story=story,
                user=request.user,
                chapter_number=next_chapter_number,
                prompt_text=prompt_text,
                voting_ends_at=voting_ends,
                status='voting'
            )
            messages.success(request, 'Your prompt has been submitted! Voting ends in 7 days.')
            return redirect('stories:story_detail', slug=story.slug)

    # Get previous chapter for context
    previous_chapter = Chapter.objects.filter(
        story=story,
        chapter_number=next_chapter_number - 1,
        status='published'
    ).first()

    context = {
        'story': story,
        'next_chapter_number': next_chapter_number,
        'existing_prompt': existing_prompt,
        'previous_chapter': previous_chapter,
    }
    return render(request, 'stories/submit_prompt.html', context)


@login_required
def vote_prompt(request, prompt_id):
    """Vote on a prompt"""
    prompt = get_object_or_404(Prompt, id=prompt_id, status='voting')

    # Check if voting is still open
    if timezone.now() > prompt.voting_ends_at:
        messages.error(request, 'Voting has ended for this prompt.')
        return redirect('stories:story_detail', slug=prompt.story.slug)

    # Check if user already voted for this chapter
    existing_vote = Vote.objects.filter(
        user=request.user,
        prompt__story=prompt.story,
        prompt__chapter_number=prompt.chapter_number
    ).first()

    if existing_vote:
        # Change vote
        if existing_vote.prompt != prompt:
            existing_vote.delete()
            Vote.objects.create(user=request.user, prompt=prompt)
            messages.success(request, 'Your vote has been changed!')
        else:
            messages.info(request, 'You already voted for this prompt.')
    else:
        # New vote
        Vote.objects.create(user=request.user, prompt=prompt)
        messages.success(request, 'Vote recorded!')

    return redirect('stories:story_detail', slug=prompt.story.slug)


@login_required
def subscribe_story(request, slug):
    """Subscribe/unsubscribe to story updates"""
    story = get_object_or_404(Story, slug=slug)

    if request.user in story.subscribers.all():
        story.subscribers.remove(request.user)
        messages.success(request, f'Unsubscribed from "{story.title}"')
    else:
        story.subscribers.add(request.user)
        messages.success(request, f'Subscribed to "{story.title}"! You\'ll get notified of new chapters.')

    return redirect('stories:story_detail', slug=story.slug)


@login_required
def create_story_pitch(request):
    """Create a new story pitch for community voting"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        genre = request.POST.get('genre', 'fantasy')
        language = request.POST.get('language', 'en')

        # Story Framework fields (optional)
        characters = request.POST.get('characters', '').strip()
        story_outline = request.POST.get('story_outline', '').strip()
        world_building = request.POST.get('world_building', '').strip()
        themes = request.POST.get('themes', '').strip()
        planned_chapters = request.POST.get('planned_chapters', '').strip()
        writing_style_notes = request.POST.get('writing_style_notes', '').strip()

        if not title or not description:
            messages.error(request, 'Title and description are required.')
        elif len(description) < 100:
            messages.error(request, 'Description must be at least 100 characters.')
        else:
            story = Story.objects.create(
                title=title,
                description=description,
                genre=genre,
                language=language,
                created_by=request.user,
                status='pitch',
                # Story Framework fields
                characters=characters,
                story_outline=story_outline,
                world_building=world_building,
                themes=themes,
                planned_chapters=int(planned_chapters) if planned_chapters else None,
                writing_style_notes=writing_style_notes,
            )
            # Auto-upvote your own pitch
            story.upvoters.add(request.user)
            messages.success(request, f'Story pitch "{title}" created! Get 10 votes to activate it.')
            return redirect('stories:homepage')

    context = {
        'genre_choices': Story.GENRE_CHOICES,
        'language_choices': Story.LANGUAGE_CHOICES,
    }
    return render(request, 'stories/create_pitch.html', context)


@login_required
def upvote_story(request, slug):
    """Upvote/remove upvote from a story pitch"""
    story = get_object_or_404(Story, slug=slug)

    if request.user in story.upvoters.all():
        story.upvoters.remove(request.user)
        messages.success(request, f'Removed upvote from "{story.title}"')
    else:
        story.upvoters.add(request.user)
        messages.success(request, f'Upvoted "{story.title}"!')

        # Check if story reached vote threshold
        if story.upvote_count >= story.votes_needed and story.status == 'pitch':
            story.status = 'active'
            story.save()
            messages.success(request, f'🎉 "{story.title}" is now active! Start submitting chapter prompts!')

    return redirect('stories:homepage')


@login_required
def add_comment(request, slug, chapter_number):
    """Add a comment to a chapter"""
    if request.method != 'POST':
        return redirect('stories:chapter_detail', slug=slug, chapter_number=chapter_number)

    story = get_object_or_404(Story, slug=slug)
    chapter = get_object_or_404(Chapter, story=story, chapter_number=chapter_number, status='published')

    content = request.POST.get('content', '').strip()

    if not content:
        messages.error(request, 'Comment cannot be empty.')
    elif len(content) > 1000:
        messages.error(request, 'Comment must be 1000 characters or less.')
    else:
        Comment.objects.create(
            chapter=chapter,
            user=request.user,
            content=content
        )
        messages.success(request, 'Your comment has been posted!')

    return redirect('stories:chapter_detail', slug=slug, chapter_number=chapter_number)


# ===== Personal Story Views =====

@login_required
def my_stories(request):
    """List user's personal stories (including published ones)"""
    # Get both personal stories AND collaborative stories created by this user
    # (collaborative stories are personal stories that have been published)
    my_stories_list = Story.objects.filter(
        created_by=request.user
    ).filter(
        Q(story_type='personal') |
        Q(story_type='collaborative', created_by=request.user)
    ).annotate(
        chapter_count=Count('chapters', filter=Q(chapters__status='published'))
    ).order_by('-updated_at')

    context = {
        'personal_stories': my_stories_list,
    }
    return render(request, 'stories/my_stories.html', context)


@login_required
def create_personal_story(request):
    """Create a new personal story"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        genre = request.POST.get('genre', 'fantasy')
        language = request.POST.get('language', 'en')

        # Story Framework fields (optional)
        characters = request.POST.get('characters', '').strip()
        story_outline = request.POST.get('story_outline', '').strip()
        world_building = request.POST.get('world_building', '').strip()
        themes = request.POST.get('themes', '').strip()
        planned_chapters = request.POST.get('planned_chapters', '').strip()
        writing_style_notes = request.POST.get('writing_style_notes', '').strip()

        if not title or not description:
            messages.error(request, 'Title and description are required.')
        elif len(description) < 50:
            messages.error(request, 'Description must be at least 50 characters.')
        else:
            story = Story.objects.create(
                story_type='personal',
                title=title,
                description=description,
                genre=genre,
                language=language,
                created_by=request.user,
                status='active',
                # Story Framework fields
                characters=characters,
                story_outline=story_outline,
                world_building=world_building,
                themes=themes,
                planned_chapters=int(planned_chapters) if planned_chapters else None,
                writing_style_notes=writing_style_notes,
            )
            messages.success(request, f'Personal story "{title}" created! Start writing your first chapter.')
            return redirect('stories:continue_personal_story', slug=story.slug)

    context = {
        'genre_choices': Story.GENRE_CHOICES,
        'language_choices': Story.LANGUAGE_CHOICES,
    }
    return render(request, 'stories/create_personal_story.html', context)


@login_required
def continue_personal_story(request, slug):
    """Continue writing a personal story - split view with last chapter and prompt editor"""
    story = get_object_or_404(Story, slug=slug, story_type='personal', created_by=request.user)

    # Get the last published chapter
    last_chapter = story.chapters.filter(status='published').order_by('-chapter_number').first()
    next_chapter_number = story.current_chapter_number

    # Handle POST request - generate new chapter
    if request.method == 'POST':
        prompt_text = request.POST.get('prompt_text', '').strip()

        if not prompt_text:
            messages.error(request, 'Prompt cannot be empty.')
        elif len(prompt_text) > 3000:
            messages.error(request, 'Prompt must be 3000 characters or less.')
        else:
            # Check if user has enough credits
            profile = request.user.profile
            if not profile.has_credits(1):
                messages.error(request, 'Not enough credits! You need 1 credit to generate a chapter.')
                return redirect('stories:credits_dashboard')

            # Deduct credit before generation
            if not profile.deduct_credits(1):
                messages.error(request, 'Failed to deduct credits. Please try again.')
                return redirect('stories:continue_personal_story', slug=story.slug)

            # Generate chapter using AI
            previous_chapters = story.chapters.filter(status='published').order_by('-chapter_number')
            result = generate_chapter(story, prompt_text, previous_chapters)

            if 'error' in result:
                # Refund credit on error
                profile.add_credits(1, source='earned')
                CreditTransaction.objects.create(
                    user=request.user,
                    amount=1,
                    transaction_type='refund',
                    description=f'Refund for failed chapter generation: {result["error"][:100]}',
                    story=story,
                    balance_after=profile.credits
                )
                messages.error(request, result['error'])
            else:
                # Create and publish the chapter
                chapter = Chapter.objects.create(
                    story=story,
                    chapter_number=next_chapter_number,
                    title=result['title'],
                    content=result['content'],
                    status='published',
                    published_at=timezone.now()
                )
                story.updated_at = timezone.now()
                story.save()

                # Record transaction
                CreditTransaction.objects.create(
                    user=request.user,
                    amount=-1,
                    transaction_type='spent',
                    description=f'Generated chapter {next_chapter_number} for "{story.title}"',
                    story=story,
                    chapter=chapter,
                    balance_after=profile.credits
                )

                messages.success(request, f'Chapter {next_chapter_number} has been generated! You have {profile.credits} credits remaining.')
                return redirect('stories:chapter_detail', slug=story.slug, chapter_number=next_chapter_number)

    context = {
        'story': story,
        'last_chapter': last_chapter,
        'next_chapter_number': next_chapter_number,
        'user_credits': request.user.profile.credits,
    }
    return render(request, 'stories/continue_personal_story.html', context)


@login_required
def publish_story(request, slug):
    """Publish a personal story to the community"""
    if request.method != 'POST':
        return redirect('stories:my_stories')

    story = get_object_or_404(Story, slug=slug, story_type='personal', created_by=request.user)

    # Check if story has at least one chapter
    if story.total_chapters == 0:
        messages.error(request, 'You need to write at least one chapter before publishing.')
        return redirect('stories:my_stories')

    # Convert to collaborative story
    story.story_type = 'collaborative'
    story.status = 'active'
    story.save()

    messages.success(request, f'🎉 "{story.title}" has been published to the community! Others can now read and vote on prompts.')
    return redirect('stories:story_detail', slug=story.slug)


@login_required
def mark_complete(request, slug):
    """Mark a story as complete (personal or collaborative)"""
    if request.method != 'POST':
        return redirect('stories:story_detail', slug=slug)

    story = get_object_or_404(Story, slug=slug, created_by=request.user)

    # Check if already completed
    if story.status == 'completed':
        messages.info(request, 'This story is already marked as complete.')
        return redirect('stories:story_detail', slug=slug)

    # Mark as completed
    story.status = 'completed'
    story.save()

    messages.success(request, f'"{story.title}" has been marked as complete! No new prompts can be submitted.')
    return redirect('stories:story_detail', slug=story.slug)


@login_required
def publish_to_community(request, slug):
    """Convert a personal story to collaborative story"""
    if request.method != 'POST':
        return redirect('stories:story_detail', slug=slug)

    story = get_object_or_404(Story, slug=slug, created_by=request.user)

    # Verify it's a personal story
    if story.story_type != 'personal':
        messages.error(request, 'Only personal stories can be published to the community.')
        return redirect('stories:story_detail', slug=slug)

    # Verify story has at least one chapter
    if story.total_chapters == 0:
        messages.error(request, 'You need to write at least one chapter before publishing to the community.')
        return redirect('stories:story_detail', slug=slug)

    # Convert to collaborative
    story.story_type = 'collaborative'
    story.save()

    messages.success(request, f'"{story.title}" has been published to the community! Users can now submit and vote on prompts for future chapters.')
    return redirect('stories:story_detail', slug=story.slug)


@login_required
def credits_dashboard(request):
    """Credits dashboard showing balance and transaction history"""
    from users.models import CreditPackage

    profile = request.user.profile
    transactions = request.user.credit_transactions.all()[:20]  # Last 20 transactions
    packages = CreditPackage.objects.filter(is_active=True).order_by('display_order')

    context = {
        'profile': profile,
        'transactions': transactions,
        'packages': packages,
    }
    return render(request, 'stories/credits_dashboard.html', context)


def submit_feedback(request):
    """Submit feedback or bug report"""
    if request.method == 'POST':
        feedback = Feedback()

        # Save user if authenticated
        if request.user.is_authenticated:
            feedback.user = request.user
        else:
            # Save email for non-authenticated users
            feedback.email = request.POST.get('email', '')

        feedback.type = request.POST.get('type', 'feedback')
        feedback.subject = request.POST.get('subject', '')
        feedback.description = request.POST.get('description', '')

        # Handle screenshot upload
        if request.FILES.get('screenshot'):
            feedback.screenshot = request.FILES['screenshot']

        feedback.save()

        messages.success(request, 'Thank you for your feedback! We will review it soon.')
        return redirect('stories:submit_feedback')

    return render(request, 'stories/submit_feedback.html')


@login_required
def feedback_admin(request):
    """Admin view to manage feedback submissions"""
    # Only allow staff/superusers
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('stories:homepage')

    # Handle status updates
    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        feedback = get_object_or_404(Feedback, id=feedback_id)

        # Update status
        if 'status' in request.POST:
            feedback.status = request.POST.get('status')

        # Update admin notes
        if 'admin_notes' in request.POST:
            feedback.admin_notes = request.POST.get('admin_notes')

        feedback.save()
        messages.success(request, f'Feedback #{feedback.id} updated successfully.')
        return redirect('stories:feedback_admin')

    # Filter feedbacks
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')

    feedbacks = Feedback.objects.all()

    if status_filter != 'all':
        feedbacks = feedbacks.filter(status=status_filter)

    if type_filter != 'all':
        feedbacks = feedbacks.filter(type=type_filter)

    # Get counts for filters
    status_counts = {
        'all': Feedback.objects.count(),
        'new': Feedback.objects.filter(status='new').count(),
        'in_progress': Feedback.objects.filter(status='in_progress').count(),
        'resolved': Feedback.objects.filter(status='resolved').count(),
        'closed': Feedback.objects.filter(status='closed').count(),
    }

    context = {
        'feedbacks': feedbacks,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'status_counts': status_counts,
        'status_choices': Feedback.STATUS_CHOICES,
        'type_choices': Feedback.TYPE_CHOICES,
    }
    return render(request, 'stories/feedback_admin.html', context)
