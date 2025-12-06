"""
SEO utilities for generating meta tags and structured data for PlotVote
"""
from django.conf import settings


def get_story_meta(story):
    """
    Generate meta tags for a story page

    Args:
        story: Story model instance

    Returns:
        dict: Meta tag data including title, description, keywords, image, url
    """
    # Create SEO-optimized title (50-60 chars ideal)
    title = f"{story.title} - {story.get_genre_display()} Story | PlotVote"

    # Description (150-160 chars ideal)
    description = story.description[:157] + "..." if len(story.description) > 160 else story.description

    # Use cover image if available, otherwise default
    if story.cover_image:
        image_url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}{story.cover_image.url}"
    else:
        image_url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/static/images/default-story-cover.png"

    # Keywords combining genre, type, and title
    keywords = f"{story.get_genre_display()}, collaborative story, AI-generated fiction, interactive storytelling, {story.title}"

    # Canonical URL
    url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/"

    return {
        'title': title,
        'description': description,
        'keywords': keywords,
        'image': image_url,
        'url': url,
        'type': 'article',
    }


def get_chapter_meta(chapter):
    """
    Generate meta tags for a chapter page

    Args:
        chapter: Chapter model instance

    Returns:
        dict: Meta tag data for the chapter
    """
    story = chapter.story

    # Title including chapter number and story title
    title = f"{story.title} - Chapter {chapter.chapter_number}"
    if chapter.title:
        title += f": {chapter.title}"
    title += " | PlotVote"

    # Use first 160 chars of chapter content as description
    if chapter.content:
        description = chapter.content[:157] + "..." if len(chapter.content) > 160 else chapter.content
        # Remove excessive whitespace
        description = ' '.join(description.split())
    else:
        description = f"Read chapter {chapter.chapter_number} of {story.title}"

    # Keywords
    keywords = f"{story.get_genre_display()}, chapter {chapter.chapter_number}, {story.title}, story chapter"

    # Use story's cover image
    image = get_story_meta(story)['image']

    # Canonical URL
    url = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/chapter/{chapter.chapter_number}/"

    return {
        'title': title,
        'description': description,
        'keywords': keywords,
        'image': image,
        'url': url,
        'type': 'article',
    }


def get_structured_data_story(story):
    """
    Generate JSON-LD structured data for a story

    Args:
        story: Story model instance

    Returns:
        dict: JSON-LD structured data
    """
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
            "userInteractionCount": story.upvoters.count() if hasattr(story, 'upvoters') else 0
        },
        "image": get_story_meta(story)['image'],
        "inLanguage": story.language if hasattr(story, 'language') else "en",
    }


def get_structured_data_chapter(chapter):
    """
    Generate JSON-LD structured data for a chapter

    Args:
        chapter: Chapter model instance

    Returns:
        dict: JSON-LD structured data
    """
    story = chapter.story

    return {
        "@context": "https://schema.org",
        "@type": "Chapter",
        "name": f"Chapter {chapter.chapter_number}" + (f": {chapter.title}" if chapter.title else ""),
        "position": chapter.chapter_number,
        "text": chapter.content[:500] + "..." if len(chapter.content) > 500 else chapter.content,
        "isPartOf": {
            "@type": "CreativeWork",
            "name": story.title,
            "url": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/"
        },
        "author": {
            "@type": "Person",
            "name": story.created_by.username
        },
        "datePublished": chapter.created_at.isoformat(),
        "url": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/story/{story.slug}/chapter/{chapter.chapter_number}/",
    }


def get_structured_data_organization():
    """
    Generate JSON-LD for PlotVote organization/website

    Returns:
        dict: JSON-LD organization data
    """
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


def get_structured_data_breadcrumbs(items):
    """
    Generate JSON-LD breadcrumb navigation

    Args:
        items: List of tuples (name, url) for breadcrumb trail

    Returns:
        dict: JSON-LD breadcrumb data

    Example:
        items = [
            ("Home", "https://plotvote.com/"),
            ("Fantasy Stories", "https://plotvote.com/genre/fantasy/"),
            ("The Dragon's Quest", "https://plotvote.com/story/the-dragons-quest/"),
        ]
    """
    breadcrumb_list = []

    for position, (name, url) in enumerate(items, start=1):
        breadcrumb_list.append({
            "@type": "ListItem",
            "position": position,
            "name": name,
            "item": url
        })

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_list
    }
