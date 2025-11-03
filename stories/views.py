"""
Views for PlotVote stories app
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import Story, Chapter, Prompt, Vote, Comment
from .ai_generator import generate_chapter


def homepage(request):
    """Homepage showing active stories and pitched stories"""
    # Get language filter from query params
    language_filter = request.GET.get('language', '')

    # Base querysets
    active_stories_qs = Story.objects.filter(status='active')
    pitched_stories_qs = Story.objects.filter(status='pitch')

    # Apply language filter if specified
    if language_filter:
        active_stories_qs = active_stories_qs.filter(language=language_filter)
        pitched_stories_qs = pitched_stories_qs.filter(language=language_filter)

    # Active stories (ready for chapter prompts)
    active_stories = active_stories_qs.annotate(
        subscriber_count_annotated=Count('subscribers')
    ).order_by('-is_featured', '-created_at')

    # Pitched stories (community voting)
    pitched_stories = pitched_stories_qs.annotate(
        upvote_count_annotated=Count('upvoters')
    ).order_by('-upvote_count_annotated', '-created_at')[:6]  # Top 6

    context = {
        'active_stories': active_stories,
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
        elif len(prompt_text) > 500:
            messages.error(request, 'Prompt must be 500 characters or less.')
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
                status='pitch'
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
    """List user's personal stories"""
    personal_stories = Story.objects.filter(
        story_type='personal',
        created_by=request.user
    ).annotate(
        chapter_count=Count('chapters', filter=Q(chapters__status='published'))
    ).order_by('-updated_at')

    context = {
        'personal_stories': personal_stories,
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
                status='active'
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
        elif len(prompt_text) > 1000:
            messages.error(request, 'Prompt must be 1000 characters or less.')
        else:
            # Generate chapter using AI
            previous_chapters = story.chapters.filter(status='published').order_by('-chapter_number')
            result = generate_chapter(story, prompt_text, previous_chapters)

            if 'error' in result:
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

                messages.success(request, f'Chapter {next_chapter_number} has been generated!')
                return redirect('stories:chapter_detail', slug=story.slug, chapter_number=next_chapter_number)

    context = {
        'story': story,
        'last_chapter': last_chapter,
        'next_chapter_number': next_chapter_number,
    }
    return render(request, 'stories/continue_personal_story.html', context)
