from django.contrib import admin
from .models import Story, Chapter, Prompt, Vote, Comment


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'language', 'status', 'created_by', 'upvote_count', 'total_chapters', 'created_at']
    list_filter = ['genre', 'language', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'upvote_count']
    filter_horizontal = ['subscribers', 'upvoters']
    actions = ['activate_story']

    def activate_story(self, request, queryset):
        """Manually activate selected stories"""
        for story in queryset:
            if story.status == 'pitch':
                story.status = 'active'
                story.save()
        self.message_user(request, f'{queryset.count()} story/stories activated.')
    activate_story.short_description = 'Activate selected stories'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['story', 'chapter_number', 'title', 'word_count', 'status', 'published_at']
    list_filter = ['status', 'story', 'published_at']
    search_fields = ['title', 'content', 'story__title']
    readonly_fields = ['word_count', 'read_time_minutes', 'created_at']


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['story', 'chapter_number', 'user', 'vote_count', 'status', 'created_at', 'voting_ends_at']
    list_filter = ['status', 'story', 'created_at']
    search_fields = ['prompt_text', 'user__username', 'story__title']
    readonly_fields = ['vote_count', 'created_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'prompt', 'created_at']
    list_filter = ['created_at', 'prompt__story']
    search_fields = ['user__username', 'prompt__prompt_text']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'chapter', 'created_at']
    list_filter = ['created_at', 'chapter__story']
    search_fields = ['content', 'user__username', 'chapter__title']
    readonly_fields = ['created_at', 'updated_at']
