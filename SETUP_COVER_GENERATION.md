# Cover Image Generation Setup Guide

## Overview
PlotVote now supports AI-powered cover image generation using OpenAI's DALL-E 3. This feature allows users to generate professional book covers when creating personal stories or pitching story ideas.

## Prerequisites
- OpenAI API account
- OpenAI API key with access to DALL-E 3

## Configuration Steps

### 1. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click "Create new secret key"
5. Copy the API key (you won't be able to see it again!)

### 2. Add API Key to Django Settings

Open your `plotvote/settings.py` file and add the following:

```python
# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
```

### 3. Set Environment Variable

#### Option A: Using .env file (Recommended for development)

1. Install python-dotenv if not already installed:
```bash
pip install python-dotenv
```

2. Create a `.env` file in your project root:
```bash
touch .env
```

3. Add your API key to `.env`:
```
OPENAI_API_KEY=sk-your-api-key-here
```

4. Make sure `.env` is in your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

5. Load environment variables in `settings.py` (add at the top):
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Option B: Using system environment variable

**Linux/Mac:**
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

Add to `~/.bashrc` or `~/.zshrc` to make it permanent:
```bash
echo "export OPENAI_API_KEY='sk-your-api-key-here'" >> ~/.bashrc
source ~/.bashrc
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

#### Option C: For production (Heroku, AWS, etc.)

Set the environment variable in your hosting platform:

**Heroku:**
```bash
heroku config:set OPENAI_API_KEY=sk-your-api-key-here
```

**AWS Elastic Beanstalk:**
- Go to Configuration > Software
- Add environment property: `OPENAI_API_KEY` = `sk-your-api-key-here`

**Docker:**
Add to your `docker-compose.yml`:
```yaml
environment:
  - OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Install Required Python Package

Make sure you have the OpenAI Python package installed:

```bash
pip install openai
```

Add to your `requirements.txt`:
```
openai>=1.0.0
```

### 5. Test the Configuration

Run Python shell:
```bash
python manage.py shell
```

Test the API connection:
```python
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Test with a simple generation
response = client.images.generate(
    model="dall-e-3",
    prompt="A beautiful fantasy book cover with a dragon",
    size="1024x1024",
    quality="standard",
    n=1,
)

print("Success! Image URL:", response.data[0].url)
```

If you see an image URL, the configuration is working!

### 6. Run Database Migrations (if needed)

Ensure the Story model's cover_image field is properly migrated:

```bash
python manage.py makemigrations
python manage.py migrate
```

## How It Works

### User Flow

1. User navigates to "Create Personal Story" or "Pitch a Story"
2. User fills in title and description
3. User clicks "Generate AI Cover Image" button
4. JavaScript makes AJAX call to `/generate-cover/` endpoint
5. Backend generates cover using DALL-E 3
6. Generated image URL is returned and displayed as preview
7. When user submits form, cover is downloaded and saved to story

### Technical Flow

```
User clicks "Generate AI Cover"
        ↓
JavaScript (generateCover())
        ↓
POST /generate-cover/
        ↓
views.generate_cover_image()
        ↓
cover_generator.generate_story_cover()
        ↓
OpenAI API (DALL-E 3)
        ↓
Returns image URL
        ↓
Displayed in browser
        ↓
User submits story form
        ↓
views.create_personal_story() / create_story_pitch()
        ↓
cover_generator.download_and_save_cover()
        ↓
Image saved to media/story_covers/
        ↓
Story created with cover
```

## Files Modified

### New Files Created:
- `stories/cover_generator.py` - Core cover generation logic
- `SETUP_COVER_GENERATION.md` - This setup guide

### Modified Files:
- `stories/views.py` - Added generate_cover_image view, updated story creation views
- `stories/urls.py` - Added generate-cover URL pattern
- `stories/templates/stories/create_personal_story.html` - Added cover generation UI
- `stories/templates/stories/create_pitch.html` - Added cover generation UI

## Cost Information

### DALL-E 3 Pricing (as of 2024):
- **Standard Quality (1024x1024):** $0.040 per image
- **HD Quality (1024x1024):** $0.080 per image

### Example Costs:
- 100 users generating covers: $4.00
- 1,000 users: $40.00
- 10,000 users: $400.00

### Cost Optimization Tips:

1. **Use Standard Quality:** The default configuration uses "standard" quality which is half the price of "hd"

2. **Rate Limiting:** Consider implementing rate limiting to prevent abuse:
```python
# In views.py
from django.core.cache import cache

def generate_cover_image(request):
    # Rate limit: 5 generations per user per day
    cache_key = f'cover_gen_{request.user.id}'
    count = cache.get(cache_key, 0)

    if count >= 5:
        return JsonResponse({
            'success': False,
            'error': 'Daily limit reached. You can generate 5 covers per day.'
        })

    cache.set(cache_key, count + 1, 86400)  # 24 hours

    # ... rest of generation logic
```

3. **Premium Feature:** Make cover generation a premium-only feature:
```python
def generate_cover_image(request):
    if not request.user.profile.has_active_subscription():
        return JsonResponse({
            'success': False,
            'error': 'Cover generation is a premium feature. Upgrade to generate covers!'
        })
```

4. **Credits System:** Charge credits for cover generation (already in place for chapters)

## Monitoring & Logging

The cover generation logs warnings when image download/save fails. To monitor:

```bash
# View Django logs
tail -f logs/django.log | grep "cover"
```

Monitor costs in OpenAI Dashboard:
https://platform.openai.com/usage

## Troubleshooting

### Error: "OPENAI_API_KEY not configured"
- Check that environment variable is set
- Restart Django server after setting env var
- Verify `settings.OPENAI_API_KEY` has a value

### Error: "Failed to generate cover"
- Check OpenAI API key is valid
- Verify account has DALL-E 3 access
- Check API usage limits/billing
- View detailed error in Django logs

### Error: "Failed to download image"
- Check internet connection
- Verify server can make outbound HTTPS requests
- Check media directory permissions

### Image not appearing after story creation
- Check `MEDIA_ROOT` and `MEDIA_URL` in settings
- Verify media files are being served correctly
- Check story.cover_image field in database

## Security Considerations

1. **Never commit API keys to Git**
   - Use `.env` file (add to `.gitignore`)
   - Use environment variables

2. **Rate Limiting**
   - Implement rate limits to prevent abuse
   - See cost optimization section above

3. **Input Validation**
   - Already implemented: title and description validation
   - Prevents malicious prompts

4. **Content Safety**
   - DALL-E 3 has built-in content policy filters
   - Inappropriate content requests are automatically rejected

## Production Checklist

- [ ] OpenAI API key added to environment variables
- [ ] Environment variables secured (not in code)
- [ ] Rate limiting implemented (optional but recommended)
- [ ] Error logging configured
- [ ] Media files serving configured properly
- [ ] Backups include media directory
- [ ] Cost monitoring alerts set up (OpenAI dashboard)
- [ ] Consider premium-only or credit-based access

## Support

If you encounter issues:

1. Check Django logs for detailed errors
2. Verify OpenAI API status: https://status.openai.com/
3. Review OpenAI API documentation: https://platform.openai.com/docs/guides/images
4. Check your API usage and billing: https://platform.openai.com/usage

## Feature Usage

### For Users:
1. Create a new story (personal or pitch)
2. Fill in title and description (required)
3. Click "Generate AI Cover Image"
4. Wait 3-5 seconds for generation
5. Preview the generated cover
6. Click "Regenerate" if not satisfied
7. Submit the form to create story with cover

### For Developers:
To use cover generation programmatically:

```python
from stories.cover_generator import generate_and_save_cover

# Generate and save cover for existing story
success, message, image_url = generate_and_save_cover(
    story,
    size="1024x1024",  # or "1792x1024" for landscape
    quality="standard"  # or "hd" for higher quality
)

if success:
    print(f"Cover generated: {image_url}")
else:
    print(f"Error: {message}")
```

## Future Enhancements

Potential improvements:
- [ ] Style selector (realistic, artistic, minimalist, etc.)
- [ ] Multiple cover variations to choose from
- [ ] Cover editing/cropping tools
- [ ] Custom prompt editing before generation
- [ ] HD quality option for premium users
- [ ] Cover gallery (show user's generated covers)
- [ ] Regenerate cover for existing stories
- [ ] AI-generated cover text/title overlay
