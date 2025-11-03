"""
Database models for PlotVote stories, chapters, prompts, and votes
"""
import re
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


def count_words(text):
    """
    Count words in text, handling both English and CJK (Chinese, Japanese, Korean) languages

    For CJK characters: each character is counted as one word
    For other text: words are split by whitespace
    """
    if not text:
        return 0

    # Pattern to match CJK characters (Chinese, Japanese, Korean)
    cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+')

    # Find all CJK characters
    cjk_chars = cjk_pattern.findall(text)
    cjk_count = sum(len(chars) for chars in cjk_chars)

    # Remove CJK characters and count remaining words
    non_cjk_text = cjk_pattern.sub(' ', text)
    non_cjk_words = [word for word in non_cjk_text.split() if word.strip()]
    non_cjk_count = len(non_cjk_words)

    return cjk_count + non_cjk_count


def calculate_read_time(word_count):
    """
    Calculate reading time in minutes

    Assumes:
    - English/non-CJK: 200 words per minute
    - CJK characters: counted as words, same rate
    """
    return max(1, word_count // 200)


class Story(models.Model):
    """A collaborative story written by AI based on community votes"""

    GENRE_CHOICES = [
        ('fantasy', 'Fantasy'),
        ('scifi', 'Science Fiction'),
        ('romance', 'Romance'),
        ('mystery', 'Mystery'),
        ('thriller', 'Thriller'),
        ('horror', 'Horror'),
        ('adventure', 'Adventure'),
        ('literary', 'Literary Fiction'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pitch', 'Pitch - Community Voting'),
        ('active', 'Active - Accepting Chapter Prompts'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh', 'Chinese'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('ar', 'Arabic'),
    ]

    STORY_TYPE_CHOICES = [
        ('collaborative', 'Collaborative Story'),
        ('personal', 'Personal Story'),
    ]

    story_type = models.CharField(max_length=20, choices=STORY_TYPE_CHOICES, default='collaborative', help_text="Type of story")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField(help_text="Brief description of the story premise")
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='fantasy')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en', help_text="Story language")
    cover_image = models.ImageField(upload_to='story_covers/', blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_stories')
    upvoters = models.ManyToManyField(User, related_name='upvoted_stories', blank=True, help_text="Users who upvoted this story pitch")
    subscribers = models.ManyToManyField(User, related_name='subscribed_stories', blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pitch', help_text="Story status")
    is_featured = models.BooleanField(default=False)
    votes_needed = models.PositiveIntegerField(default=10, help_text="Votes needed to activate story")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stories"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            # If slugify produces empty string (e.g., Chinese characters), use fallback
            if not base_slug:
                import uuid
                base_slug = f"story-{uuid.uuid4().hex[:8]}"

            # Ensure uniqueness
            slug = base_slug
            counter = 1
            while Story.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stories:story_detail', kwargs={'slug': self.slug})

    @property
    def total_chapters(self):
        return self.chapters.filter(status='published').count()

    @property
    def current_chapter_number(self):
        """Next chapter number to be written"""
        return self.total_chapters + 1

    @property
    def subscriber_count(self):
        return self.subscribers.count()

    @property
    def upvote_count(self):
        return self.upvoters.count()

    @property
    def is_active(self):
        """Backwards compatibility"""
        return self.status == 'active'


class Chapter(models.Model):
    """A chapter in a story, generated by AI from winning prompt"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generating', 'Generating'),
        ('published', 'Published'),
    ]

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="AI-generated chapter content")

    prompt_used = models.ForeignKey('Prompt', on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_chapter')

    word_count = models.PositiveIntegerField(default=0)
    read_time_minutes = models.PositiveIntegerField(default=0, help_text="Estimated reading time")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['story', 'chapter_number']
        unique_together = ['story', 'chapter_number']

    def __str__(self):
        return f"{self.story.title} - Chapter {self.chapter_number}: {self.title}"

    def save(self, *args, **kwargs):
        # Calculate word count if content exists
        if self.content:
            self.word_count = count_words(self.content)
            self.read_time_minutes = calculate_read_time(self.word_count)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stories:chapter_detail', kwargs={
            'slug': self.story.slug,
            'chapter_number': self.chapter_number
        })


class Prompt(models.Model):
    """User-submitted prompt for next chapter direction"""

    STATUS_CHOICES = [
        ('active', 'Active'),  # Currently accepting votes
        ('voting', 'Voting'),  # In voting period
        ('winner', 'Winner'),  # Won the vote, chapter generated
        ('rejected', 'Rejected'),  # Lost the vote
        ('archived', 'Archived'),  # Old prompt
    ]

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='prompts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts')

    chapter_number = models.PositiveIntegerField(help_text="Which chapter this prompt is for")
    prompt_text = models.TextField(
        max_length=500,
        help_text="What should happen in the next chapter? (max 500 characters)"
    )

    vote_count = models.IntegerField(default=0, help_text="Cached vote count for performance")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    voting_ends_at = models.DateTimeField(help_text="When voting closes for this prompt")

    class Meta:
        ordering = ['-vote_count', 'created_at']
        unique_together = ['story', 'chapter_number', 'user']  # One prompt per user per chapter

    def __str__(self):
        return f"{self.story.title} Ch.{self.chapter_number} by {self.user.username}: {self.prompt_text[:50]}"

    def update_vote_count(self):
        """Update cached vote count"""
        self.vote_count = self.votes.count()
        self.save(update_fields=['vote_count'])


class Vote(models.Model):
    """User vote on a prompt"""

    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['prompt', 'user']  # One vote per user per prompt
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} voted for prompt {self.prompt.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update prompt vote count
        self.prompt.update_vote_count()

    def delete(self, *args, **kwargs):
        prompt = self.prompt
        super().delete(*args, **kwargs)
        # Update prompt vote count after deletion
        prompt.update_vote_count()


class Comment(models.Model):
    """User comments on chapters"""

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    content = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} on {self.chapter}"
