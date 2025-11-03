# PlotVote - Community-Driven AI Stories

Community voting platform where users submit prompts, vote weekly, and AI writes the winning chapter.

## Features Implemented (MVP)

✅ **Story Management**
- Create and browse stories
- Genre categorization
- Story subscriptions

✅ **Chapter System**
- Read published chapters
- Chapter navigation (prev/next)
- Word count and reading time

✅ **Voting System**
- Submit prompts for next chapter
- Vote on community prompts
- One vote per user per chapter
- Change vote before deadline

✅ **User Features**
- Login/logout
- Subscribe to stories
- View voting status

## Tech Stack

- Django 5.2.7
- SQLite (development)
- Tailwind CSS (CDN)
- Python 3.11

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/jiegou/Downloads/plotvote
source venv/bin/activate
pip install django Pillow
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

### 3. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

### 4. Create Your First Story

1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Add a new Story:
   - Title: "The Dragon's Quest"
   - Description: "A young hero must find the ancient dragon"
   - Genre: Fantasy
   - Created by: (select your user)
   - Is active: ✓
4. Save

Now visit http://localhost:8000 and you'll see your story!

## Usage Flow

### For Users:

1. **Browse Stories** - Homepage shows all active stories
2. **Read Chapters** - Click story → view all published chapters
3. **Submit Prompt** - Suggest what happens in next chapter
4. **Vote** - Vote on your favorite prompt
5. **Subscribe** - Get notified when new chapters publish

### For Admins:

1. **Create Story** - Add via Django admin
2. **Monitor Prompts** - See all submitted prompts with vote counts
3. **Generate Chapter** - Use AI to automatically generate from winning prompt:
   ```bash
   python manage.py generate_chapter <story-slug>
   ```
   - Finds highest voted prompt automatically
   - Generates 1500-2500 word chapter using GPT-4o-mini
   - Creates title and publishes automatically

## Database Models

- **Story** - The main story container
- **Chapter** - Individual chapters (AI-generated)
- **Prompt** - User-submitted ideas for next chapter
- **Vote** - User votes on prompts
- **Comment** - Comments on chapters

## AI Chapter Generation

✅ **OpenAI Integration Complete!**

The app uses GPT-4o-mini to generate chapters from winning prompts.

### Setup:

1. **Get OpenAI API Key:**
   - Sign up at https://platform.openai.com
   - Create API key
   - Add $5-10 credit

2. **Add to .env file:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Generate Chapter:**
   ```bash
   # Automatic (uses highest voted prompt)
   python manage.py generate_chapter the-dragons-quest

   # Specific prompt ID
   python manage.py generate_chapter the-dragons-quest --prompt-id 5

   # Specific chapter number
   python manage.py generate_chapter the-dragons-quest --chapter 3
   ```

### Cost:
- ~$0.01 per chapter (2000 words)
- 100 chapters = ~$1
- Very affordable!

## Next Steps (Not Implemented Yet)

🔜 **Celery Tasks**
- Weekly voting closure
- Automatic winner selection
- Email notifications

🔜 **User Registration**
- Sign up page
- Email verification

🔜 **Enhanced Features**
- Comment system implementation
- User profiles
- Story creation by users

## Project Structure

```
plotvote/
├── manage.py
├── plotvote/          # Project settings
│   ├── settings.py
│   └── urls.py
├── stories/           # Main app
│   ├── models.py      # Database models
│   ├── views.py       # View logic
│   ├── urls.py        # URL routing
│   ├── admin.py       # Admin configuration
│   └── templates/     # HTML templates
└── templates/         # Base templates
    └── base.html
```

## Development Notes

- Currently using SQLite (switch to PostgreSQL for production)
- Tailwind CSS via CDN (consider local build for production)
- AI generation is manual (add OpenAI API next)
- No email notifications yet (add Celery + email backend)

## Testing the MVP

1. Create a story via admin
2. Create a user account
3. Submit a prompt for chapter 1
4. Vote on prompts
5. Manually create a chapter in admin (simulating AI)
6. Read the chapter
7. Submit prompt for chapter 2

---

**Built with Claude Code** 🤖
