"""
Sitemap configuration for PlotVote
Generates XML sitemap for search engine crawlers
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Story, Chapter


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        """Return list of static URL names"""
        return [
            'stories:homepage',
            'stories:create_personal_story',
            'stories:create_story_pitch',
        ]

    def location(self, item):
        """Return the URL for each item"""
        return reverse(item)


class StorySitemap(Sitemap):
    """Sitemap for published story pages"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        """Return published/active stories (exclude private personal stories)"""
        return Story.objects.filter(
            status__in=['active', 'completed', 'pitch']
        ).exclude(
            story_type='personal'  # Don't include private stories
        ).order_by('-updated_at')

    def lastmod(self, obj):
        """Return last modification date"""
        return obj.updated_at

    def location(self, obj):
        """Return the URL for each story"""
        return f'/story/{obj.slug}/'


class ChapterSitemap(Sitemap):
    """Sitemap for chapter pages"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        """Return published chapters from public stories"""
        return Chapter.objects.filter(
            status='published'
        ).filter(
            story__status__in=['active', 'completed']
        ).exclude(
            story__story_type='personal'  # Don't include chapters from private stories
        ).select_related('story').order_by('-created_at')

    def lastmod(self, obj):
        """Return creation date (chapters don't get modified)"""
        return obj.created_at

    def location(self, obj):
        """Return the URL for each chapter"""
        return f'/story/{obj.story.slug}/chapter/{obj.chapter_number}/'
