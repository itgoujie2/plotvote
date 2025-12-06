# SEO Setup Guide for PlotVote.com

Complete guide to implementing search engine optimization for PlotVote - a collaborative storytelling platform.

## Table of Contents

1. [Technical SEO Foundation](#1-technical-seo-foundation)
2. [Meta Tags & Structured Data](#2-meta-tags--structured-data)
3. [Django SEO Implementation](#3-django-seo-implementation)
4. [Content Optimization](#4-content-optimization)
5. [Performance Optimization](#5-performance-optimization)
6. [Social Media Integration](#6-social-media-integration)
7. [Sitemap & Robots.txt](#7-sitemap--robotstxt)
8. [Analytics & Search Console](#8-analytics--search-console)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)

---

## 1. Technical SEO Foundation

### 1.1 Install Django SEO Packages

```bash
pip install django-meta django-sitemap
```

Add to `requirements.txt`:
```
django-meta==2.3.0
```

### 1.2 Configure Settings

**plotvote/settings.py:**
```python
INSTALLED_APPS = [
    # ... existing apps
    'meta',
]

# SEO Settings
SITE_ID = 1
SITE_NAME = 'PlotVote'
SITE_PROTOCOL = 'https'
SITE_DOMAIN = 'plotvote.com'

# Meta defaults
META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = 'plotvote.com'
META_SITE_NAME = 'PlotVote'
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SCHEMA_ORG_PROPERTIES = True

# Default meta tags
META_DEFAULT_KEYWORDS = [
    'collaborative storytelling',
    'AI story generation',
    'interactive fiction',
    'community writing',
    'creative writing',
    'story voting',
]

META_IMAGE_URL = f"{SITE_PROTOCOL}://{SITE_DOMAIN}/static/images/plotvote-og-image.png"
```

---

## 2. Meta Tags & Structured Data

### 2.1 Base Template Meta Tags

**templates/base.html:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Primary Meta Tags -->
    <title>{% block title %}PlotVote - Collaborative AI Storytelling Platform{% endblock %}</title>
    <meta name="title" content="{% block meta_title %}PlotVote - Collaborative AI Storytelling Platform{% endblock %}">
    <meta name="description" content="{% block meta_description %}Create and vote on AI-generated stories. Join a community of writers and readers shaping interactive fiction together.{% endblock %}">
    <meta name="keywords" content="{% block meta_keywords %}collaborative storytelling, AI story generation, interactive fiction, community writing{% endblock %}">
    <meta name="author" content="PlotVote">
    <meta name="robots" content="{% block meta_robots %}index, follow{% endblock %}">

    <!-- Canonical URL -->
    <link rel="canonical" href="{% block canonical_url %}https://plotvote.com{{ request.path }}{% endblock %}">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="{% block og_type %}website{% endblock %}">
    <meta property="og:url" content="https://plotvote.com{{ request.path }}">
    <meta property="og:title" content="{% block og_title %}PlotVote - Collaborative AI Storytelling{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Create and vote on AI-generated stories. Join a community of writers and readers.{% endblock %}">
    <meta property="og:image" content="{% block og_image %}https://plotvote.com/static/images/plotvote-og-image.png{% endblock %}">
    <meta property="og:site_name" content="PlotVote">
    <meta property="og:locale" content="en_US">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://plotvote.com{{ request.path }}">
    <meta name="twitter:title" content="{% block twitter_title %}PlotVote - Collaborative AI Storytelling{% endblock %}">
    <meta name="twitter:description" content="{% block twitter_description %}Create and vote on AI-generated stories. Join a community of writers.{% endblock %}">
    <meta name="twitter:image" content="{% block twitter_image %}https://plotvote.com/static/images/plotvote-twitter-card.png{% endblock %}">
    {% if twitter_handle %}<meta name="twitter:site" content="@{{ twitter_handle }}">{% endif %}

    <!-- Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">

    <!-- Additional SEO -->
    <meta name="theme-color" content="#6366f1">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">

    {% block extra_head %}{% endblock %}
</head>
```

### 2.2 Create Social Media Images

**Required images:**
1. **Open Graph Image**: `1200x630px` - `/static/images/plotvote-og-image.png`
2. **Twitter Card**: `1200x600px` - `/static/images/plotvote-twitter-card.png`
3. **Favicon Set**: 16x16, 32x32, 180x180

**Design tips:**
- Include PlotVote logo
- Use brand colors (indigo/purple)
- Add tagline: "Collaborative AI Storytelling"
- Ensure text is readable on mobile preview

---

## 3. Django SEO Implementation

### 3.1 Create SEO Utility Module

**stories/seo_utils.py:**
```python
"""
SEO utilities for generating meta tags and structured data
"""
from django.conf import settings


def get_story_meta(story):
    """Generate meta tags for a story page"""
    title = f"{story.title} - {story.get_genre_display()} Story | PlotVote"
    description = story.description[:160] if len(story.description) > 160 else story.description

    # Use cover image if available, otherwise default
    if story.cover_image:
        image_url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}{story.cover_image.url}"
    else:
        image_url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/static/images/default-story-cover.png"

    return {
        'title': title,
        'description': description,
        'keywords': f"{story.get_genre_display()}, collaborative story, AI-generated fiction, {story.title}",
        'image': image_url,
        'url': f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/",
        'type': 'article',
    }


def get_chapter_meta(chapter):
    """Generate meta tags for a chapter page"""
    story = chapter.story
    title = f"{story.title} - Chapter {chapter.chapter_number} | PlotVote"

    # Use first 160 chars of chapter content as description
    description = chapter.content[:160] + "..." if len(chapter.content) > 160 else chapter.content

    return {
        'title': title,
        'description': description,
        'keywords': f"{story.get_genre_display()}, chapter {chapter.chapter_number}, {story.title}",
        'image': get_story_meta(story)['image'],
        'url': f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/chapter/{chapter.chapter_number}/",
        'type': 'article',
    }


def get_structured_data_story(story):
    """Generate JSON-LD structured data for a story"""
    return {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": story.title,
        "description": story.description,
        "genre": story.get_genre_display(),
        "author": {
            "@type": "Person",
            "name": story.created_by.username
        },
        "dateCreated": story.created_at.isoformat(),
        "dateModified": story.updated_at.isoformat(),
        "url": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/",
        "interactionStatistic": {
            "@type": "InteractionCounter",
            "interactionType": "https://schema.org/LikeAction",
            "userInteractionCount": story.upvoters.count()
        },
        "image": get_story_meta(story)['image'],
    }


def get_structured_data_organization():
    """Generate JSON-LD for PlotVote organization"""
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "PlotVote",
        "description": "Collaborative AI storytelling platform where communities create and vote on interactive fiction",
        "url": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/search?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        },
        "publisher": {
            "@type": "Organization",
            "name": "PlotVote",
            "logo": {
                "@type": "ImageObject",
                "url": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/static/images/plotvote-logo.png"
            }
        }
    }
```

### 3.2 Update Views with SEO Context

**stories/views.py:**
```python
from .seo_utils import get_story_meta, get_structured_data_story
import json

def story_detail(request, slug):
    story = get_object_or_404(Story, slug=slug)

    # SEO metadata
    seo_meta = get_story_meta(story)
    structured_data = get_structured_data_story(story)

    context = {
        'story': story,
        # ... existing context
        'seo_meta': seo_meta,
        'structured_data_json': json.dumps(structured_data),
    }

    return render(request, 'stories/story_detail.html', context)
```

### 3.3 Update Story Detail Template

**stories/templates/stories/story_detail.html:**
```html
{% extends 'base.html' %}

{% block title %}{{ seo_meta.title }}{% endblock %}
{% block meta_description %}{{ seo_meta.description }}{% endblock %}
{% block meta_keywords %}{{ seo_meta.keywords }}{% endblock %}

{% block og_title %}{{ seo_meta.title }}{% endblock %}
{% block og_description %}{{ seo_meta.description }}{% endblock %}
{% block og_image %}{{ seo_meta.image }}{% endblock %}
{% block og_type %}article{% endblock %}

{% block twitter_title %}{{ seo_meta.title }}{% endblock %}
{% block twitter_description %}{{ seo_meta.description }}{% endblock %}
{% block twitter_image %}{{ seo_meta.image }}{% endblock %}

{% block extra_head %}
<!-- Structured Data -->
<script type="application/ld+json">
{{ structured_data_json|safe }}
</script>
{% endblock %}

{% block content %}
<!-- Your existing content -->
{% endblock %}
```

---

## 4. Content Optimization

### 4.1 Optimize Story Titles and Descriptions

**Best practices:**
- **Title length**: 50-60 characters
- **Description length**: 150-160 characters
- **Include keywords naturally**
- **Make it compelling for users**

**Example:**
```
Good: "The Dragon's Quest - Epic Fantasy Adventure | PlotVote"
Bad: "Story #123 | PlotVote"

Good Description: "Join a young hero's journey to find the ancient dragon in this collaborative fantasy epic. Vote on plot twists and shape the story."
Bad Description: "A story about dragons."
```

### 4.2 URL Structure

**Best practices:**
- Use slugs (already implemented ✓)
- Keep URLs short and descriptive
- Use hyphens, not underscores
- Avoid dynamic parameters when possible

**Current structure (good):**
```
✓ plotvote.com/story/the-dragons-quest/
✓ plotvote.com/story/the-dragons-quest/chapter/1/
✓ plotvote.com/pitch/
```

### 4.3 Heading Structure

**Ensure proper H1-H6 hierarchy:**

```html
<!-- Homepage -->
<h1>PlotVote - Collaborative AI Storytelling</h1>
<h2>Active Stories</h2>
<h3>{{ story.title }}</h3>

<!-- Story Page -->
<h1>{{ story.title }}</h1>
<h2>About This Story</h2>
<h2>Chapters</h2>
<h3>Chapter {{ chapter.chapter_number }}: {{ chapter.title }}</h3>
```

### 4.4 Alt Text for Images

**Update all image tags:**

```html
<!-- Story covers -->
<img src="{{ story.cover_image.url }}"
     alt="{{ story.title }} - {{ story.get_genre_display }} book cover illustration">

<!-- User avatars -->
<img src="{{ user.avatar.url }}"
     alt="{{ user.username }}'s profile picture">

<!-- Icons and decorative images -->
<img src="/static/icons/bookmark.svg"
     alt="Bookmark icon"
     role="img">
```

---

## 5. Performance Optimization

### 5.1 Image Optimization

**Install Pillow and optimize images:**

```bash
pip install Pillow pillow-avif-plugin
```

**settings.py:**
```python
# Image optimization
THUMBNAIL_ALIASES = {
    'stories': {
        'cover_large': {'size': (800, 1200), 'crop': False},
        'cover_medium': {'size': (400, 600), 'crop': False},
        'cover_thumb': {'size': (200, 300), 'crop': False},
    }
}

# Enable image optimization
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
```

### 5.2 Enable Compression

**Use Django Compressor:**

```bash
pip install django-compressor
```

**settings.py:**
```python
INSTALLED_APPS += ['compressor']

COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
```

### 5.3 Enable Caching

**settings.py:**
```python
# Cache framework
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'plotvote',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Cache middleware
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # First
    # ... other middleware
    'django.middleware.cache.FetchFromCacheMiddleware',  # Last
]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'plotvote'
```

### 5.4 Database Query Optimization

**Use select_related and prefetch_related:**

```python
# stories/views.py

def homepage(request):
    # Optimize queries
    active_stories = Story.objects.filter(
        status='active'
    ).select_related(
        'created_by'
    ).prefetch_related(
        'subscribers',
        'chapters'
    ).annotate(
        subscriber_count=Count('subscribers')
    ).order_by('-created_at')

    return render(request, 'homepage.html', {'active_stories': active_stories})
```

---

## 6. Social Media Integration

### 6.1 Twitter Card Validation

1. Create Twitter account: **@PlotVoteApp**
2. Add to settings.py:
```python
TWITTER_HANDLE = 'PlotVoteApp'
```

3. Validate cards: https://cards-dev.twitter.com/validator

### 6.2 Facebook Open Graph

1. Create Facebook page for PlotVote
2. Validate: https://developers.facebook.com/tools/debug/
3. Add Facebook App ID (optional):

```html
<meta property="fb:app_id" content="YOUR_APP_ID">
```

### 6.3 Social Sharing Buttons

**Add to story_detail.html:**

```html
<div class="social-share">
    <h3>Share this story</h3>

    <!-- Twitter -->
    <a href="https://twitter.com/intent/tweet?text={{ story.title|urlencode }}&url={{ request.build_absolute_uri }}&via=PlotVoteApp"
       target="_blank"
       rel="noopener"
       class="share-btn twitter">
        Share on Twitter
    </a>

    <!-- Facebook -->
    <a href="https://www.facebook.com/sharer/sharer.php?u={{ request.build_absolute_uri }}"
       target="_blank"
       rel="noopener"
       class="share-btn facebook">
        Share on Facebook
    </a>

    <!-- LinkedIn -->
    <a href="https://www.linkedin.com/sharing/share-offsite/?url={{ request.build_absolute_uri }}"
       target="_blank"
       rel="noopener"
       class="share-btn linkedin">
        Share on LinkedIn
    </a>

    <!-- Reddit -->
    <a href="https://reddit.com/submit?url={{ request.build_absolute_uri }}&title={{ story.title|urlencode }}"
       target="_blank"
       rel="noopener"
       class="share-btn reddit">
        Share on Reddit
    </a>
</div>
```

---

## 7. Sitemap & Robots.txt

### 7.1 Create Dynamic Sitemap

**stories/sitemaps.py:**
```python
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Story, Chapter


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['stories:homepage', 'stories:create_personal_story', 'stories:create_pitch']

    def location(self, item):
        return reverse(item)


class StorySitemap(Sitemap):
    """Sitemap for story pages"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        # Only include published/active stories
        return Story.objects.filter(
            status__in=['active', 'completed']
        ).exclude(
            story_type='personal'  # Don't include private stories
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/story/{obj.slug}/'


class ChapterSitemap(Sitemap):
    """Sitemap for chapter pages"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        # Only chapters from public stories
        return Chapter.objects.filter(
            story__status__in=['active', 'completed']
        ).exclude(
            story__story_type='personal'
        ).select_related('story')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f'/story/{obj.story.slug}/chapter/{obj.chapter_number}/'
```

**plotvote/urls.py:**
```python
from django.contrib.sitemaps.views import sitemap
from stories.sitemaps import StaticViewSitemap, StorySitemap, ChapterSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'stories': StorySitemap,
    'chapters': ChapterSitemap,
}

urlpatterns = [
    # ... existing urls
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
```

### 7.2 Create robots.txt

**Create: public/robots.txt**
```txt
# PlotVote Robots.txt

User-agent: *
Allow: /
Allow: /story/
Allow: /pitch/

# Disallow private/admin areas
Disallow: /admin/
Disallow: /my-stories/
Disallow: /story/*/delete/
Disallow: /api/

# Disallow search parameters that create duplicate content
Disallow: /*?sort=
Disallow: /*?filter=
Disallow: /*?page=

# Sitemaps
Sitemap: https://plotvote.com/sitemap.xml

# Crawl-delay (optional, for aggressive bots)
Crawl-delay: 10
```

**Serve robots.txt in urls.py:**
```python
from django.views.generic import TemplateView

urlpatterns = [
    # ... existing urls
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    )),
]
```

**templates/robots.txt:**
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /my-stories/
Sitemap: https://plotvote.com/sitemap.xml
```

---

## 8. Analytics & Search Console

### 8.1 Google Analytics 4

**Sign up:** https://analytics.google.com/

**Add to base.html before </head>:**
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Track custom events:**
```html
<script>
// Track story creation
function trackStoryCreated(genre) {
    gtag('event', 'story_created', {
        'genre': genre,
        'event_category': 'engagement',
        'event_label': 'Story Creation'
    });
}

// Track chapter generation
function trackChapterGenerated(storySlug) {
    gtag('event', 'chapter_generated', {
        'story': storySlug,
        'event_category': 'engagement',
        'event_label': 'AI Chapter Generation'
    });
}

// Track votes
function trackVote(promptId) {
    gtag('event', 'prompt_vote', {
        'prompt_id': promptId,
        'event_category': 'engagement',
        'event_label': 'Prompt Voting'
    });
}
</script>
```

### 8.2 Google Search Console

**Setup steps:**

1. Go to: https://search.google.com/search-console/
2. Add property: `https://plotvote.com`
3. Verify ownership (choose method):
   - **HTML file upload** (recommended)
   - DNS verification
   - HTML tag

**HTML Tag Verification:**
```html
<!-- Add to base.html <head> -->
<meta name="google-site-verification" content="YOUR_VERIFICATION_CODE" />
```

**Submit sitemap:**
1. In Search Console, go to Sitemaps
2. Submit: `https://plotvote.com/sitemap.xml`

### 8.3 Bing Webmaster Tools

**Setup steps:**

1. Go to: https://www.bing.com/webmasters/
2. Add site: `https://plotvote.com`
3. Verify (can import from Google Search Console)
4. Submit sitemap

### 8.4 Additional Monitoring Tools

**Install:**
- **Google Tag Manager**: For easier tracking management
- **Hotjar**: User behavior analytics
- **Plausible/Fathom**: Privacy-friendly analytics alternative

---

## 9. Monitoring & Maintenance

### 9.1 SEO Monitoring Checklist

**Weekly:**
- [ ] Check Google Search Console for errors
- [ ] Monitor organic traffic in Google Analytics
- [ ] Check for broken links
- [ ] Review top performing pages

**Monthly:**
- [ ] Run site audit (use Screaming Frog or Sitebulb)
- [ ] Check page load speeds (PageSpeed Insights)
- [ ] Review and update meta descriptions
- [ ] Check mobile usability
- [ ] Monitor keyword rankings

**Quarterly:**
- [ ] Update sitemap
- [ ] Review and update content
- [ ] Analyze competitor SEO strategies
- [ ] Check backlink profile
- [ ] Update structured data

### 9.2 SEO Monitoring Tools

**Free tools:**
- Google Search Console (essential)
- Google Analytics (essential)
- Google PageSpeed Insights
- Mobile-Friendly Test
- Rich Results Test
- XML Sitemap validator

**Paid tools (optional):**
- Ahrefs ($99/mo) - Comprehensive SEO suite
- SEMrush ($119/mo) - Keyword research & competitor analysis
- Moz Pro ($99/mo) - SEO tracking and insights
- Screaming Frog ($149/yr) - Technical SEO crawler

### 9.3 Performance Monitoring

**Create monitoring script:**

**scripts/check_seo.py:**
```python
#!/usr/bin/env python
"""
SEO health check script
Run daily to monitor SEO metrics
"""
import requests
from bs4 import BeautifulSoup
import sys

def check_page(url):
    """Check basic SEO requirements for a page"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        issues = []

        # Check title
        title = soup.find('title')
        if not title:
            issues.append("Missing <title> tag")
        elif len(title.text) > 60:
            issues.append(f"Title too long ({len(title.text)} chars)")

        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            issues.append("Missing meta description")
        elif len(meta_desc.get('content', '')) > 160:
            issues.append(f"Meta description too long ({len(meta_desc.get('content', ''))} chars)")

        # Check H1
        h1 = soup.find('h1')
        if not h1:
            issues.append("Missing <h1> tag")

        # Check canonical
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            issues.append("Missing canonical URL")

        # Check Open Graph
        og_title = soup.find('meta', property='og:title')
        og_image = soup.find('meta', property='og:image')
        if not og_title:
            issues.append("Missing og:title")
        if not og_image:
            issues.append("Missing og:image")

        return {
            'url': url,
            'status_code': response.status_code,
            'issues': issues,
            'load_time': response.elapsed.total_seconds()
        }

    except Exception as e:
        return {
            'url': url,
            'error': str(e)
        }

# Check key pages
pages_to_check = [
    'https://plotvote.com/',
    'https://plotvote.com/story/the-dragons-quest/',
    'https://plotvote.com/pitch/',
]

for page in pages_to_check:
    result = check_page(page)
    print(f"\n{result['url']}")
    if 'error' in result:
        print(f"  ERROR: {result['error']}")
    else:
        print(f"  Status: {result['status_code']}")
        print(f"  Load time: {result['load_time']:.2f}s")
        if result['issues']:
            print("  Issues:")
            for issue in result['issues']:
                print(f"    - {issue}")
        else:
            print("  ✓ All checks passed")
```

**Run via cron:**
```bash
# Add to crontab
0 9 * * * /path/to/venv/bin/python /path/to/plotvote/scripts/check_seo.py >> /var/log/plotvote_seo.log 2>&1
```

### 9.4 Error Monitoring

**Setup 404 monitoring:**

**stories/views.py:**
```python
from django.core.mail import mail_admins
from django.views.defaults import page_not_found
import logging

logger = logging.getLogger(__name__)

def custom_404(request, exception):
    """Custom 404 handler with logging"""
    logger.warning(f"404 Error: {request.path} - Referrer: {request.META.get('HTTP_REFERER', 'None')}")

    # Email admins for important 404s (not bots)
    if not any(bot in request.META.get('HTTP_USER_AGENT', '').lower() for bot in ['bot', 'crawler', 'spider']):
        mail_admins(
            f'404 Error on PlotVote',
            f'Path: {request.path}\nReferrer: {request.META.get("HTTP_REFERER", "None")}\nUser Agent: {request.META.get("HTTP_USER_AGENT", "None")}'
        )

    return page_not_found(request, exception, template_name='404.html')
```

**plotvote/urls.py:**
```python
handler404 = 'stories.views.custom_404'
```

---

## 10. Launch Checklist

Before going live, verify:

### Pre-Launch SEO Checklist

**Technical:**
- [ ] All meta tags configured
- [ ] Structured data implemented
- [ ] Sitemap.xml generated and accessible
- [ ] Robots.txt configured
- [ ] Canonical URLs set correctly
- [ ] 404 pages configured
- [ ] HTTPS enabled with valid SSL certificate
- [ ] www vs non-www redirect configured
- [ ] Page load time < 3 seconds
- [ ] Mobile responsive design

**Content:**
- [ ] All pages have unique titles
- [ ] All pages have unique descriptions
- [ ] All images have alt text
- [ ] Proper heading hierarchy (H1-H6)
- [ ] Internal linking structure
- [ ] No broken links
- [ ] Content is original and valuable

**Social:**
- [ ] Open Graph tags configured
- [ ] Twitter Cards configured
- [ ] Social sharing buttons added
- [ ] Social media images created (1200x630)

**Analytics:**
- [ ] Google Analytics installed
- [ ] Google Search Console verified
- [ ] Sitemap submitted to Search Console
- [ ] Event tracking configured
- [ ] Conversion goals set up

**Validation:**
- [ ] Test meta tags: https://metatags.io/
- [ ] Validate structured data: https://validator.schema.org/
- [ ] Test Twitter cards: https://cards-dev.twitter.com/validator
- [ ] Test Open Graph: https://developers.facebook.com/tools/debug/
- [ ] Check mobile-friendly: https://search.google.com/test/mobile-friendly
- [ ] Check page speed: https://pagespeed.web.dev/

---

## 11. Advanced SEO Strategies

### 11.1 Content Marketing

**Blog integration:**
```python
# Create blog app
python manage.py startapp blog

# Blog post model with SEO fields
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    meta_description = models.CharField(max_length=160)
    content = models.TextField()
    featured_image = models.ImageField()
    published_at = models.DateTimeField()
    # ... SEO fields
```

**Content ideas for PlotVote blog:**
- "How to Write Compelling Story Prompts"
- "Top 10 Collaborative Stories on PlotVote"
- "AI Writing Tips: Making the Most of Story Generation"
- "Building Community Through Interactive Fiction"

### 11.2 Schema.org Markup

**Add breadcrumbs:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Home",
    "item": "https://plotvote.com/"
  },{
    "@type": "ListItem",
    "position": 2,
    "name": "{{ story.title }}",
    "item": "https://plotvote.com/story/{{ story.slug }}/"
  }]
}
</script>
```

**Add review schema:**
```python
def get_review_schema(story):
    """Generate review/rating schema for stories"""
    return {
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {
            "@type": "CreativeWork",
            "name": story.title
        },
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": story.average_rating,
            "bestRating": "5"
        },
        "author": {
            "@type": "Person",
            "name": story.created_by.username
        }
    }
```

### 11.3 International SEO (Future)

**For multi-language support:**
```html
<link rel="alternate" hreflang="en" href="https://plotvote.com/" />
<link rel="alternate" hreflang="es" href="https://plotvote.com/es/" />
<link rel="alternate" hreflang="zh" href="https://plotvote.com/zh/" />
<link rel="alternate" hreflang="x-default" href="https://plotvote.com/" />
```

---

## 12. Resources & Documentation

### Official Documentation
- [Google Search Central](https://developers.google.com/search)
- [Django SEO Best Practices](https://docs.djangoproject.com/en/stable/topics/performance/)
- [Schema.org](https://schema.org/)
- [Open Graph Protocol](https://ogp.me/)

### Tools
- [Google Search Console](https://search.google.com/search-console/)
- [Google Analytics](https://analytics.google.com/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Meta Tags Validator](https://metatags.io/)
- [Structured Data Validator](https://validator.schema.org/)

### Learning Resources
- [Moz Beginner's Guide to SEO](https://moz.com/beginners-guide-to-seo)
- [Google SEO Starter Guide](https://developers.google.com/search/docs/beginner/seo-starter-guide)
- [Ahrefs Blog](https://ahrefs.com/blog/)

---

## Support & Maintenance

For questions or issues:
1. Check Google Search Console for crawl errors
2. Review server logs for 404s
3. Monitor page load times
4. Keep Django and dependencies updated
5. Regularly audit SEO performance

**Last Updated:** December 2024
**Next Review:** March 2025
