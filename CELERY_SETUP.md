# Celery Setup for PlotVote

## Prerequisites

1. **Install Redis** (if not already installed):
   ```bash
   # macOS
   brew install redis

   # Ubuntu/Debian
   sudo apt-get install redis-server
   ```

2. **Start Redis**:
   ```bash
   # macOS
   brew services start redis

   # Ubuntu/Debian
   sudo service redis-server start

   # Or run in foreground
   redis-server
   ```

## Running PlotVote with Celery

You need to run **3 separate terminal windows**:

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: Django Development Server
```bash
cd /Users/jiegou/Downloads/plotvote
source venv/bin/activate
python manage.py runserver
```

### Terminal 3: Celery Worker
```bash
cd /Users/jiegou/Downloads/plotvote
source venv/bin/activate
celery -A plotvote worker --loglevel=info
```

## How It Works

1. When a **Prompt** status is changed to `"winner"` in the admin panel, a Django signal automatically triggers
2. The signal queues a Celery task: `generate_chapter_from_prompt`
3. The Celery worker picks up the task and:
   - Fetches the winning prompt
   - Calls OpenAI API to generate the chapter
   - Creates a new Chapter object with the AI-generated content
   - Sets the chapter status to 'published'

## Testing the Auto-Generation

1. Create a story and activate it (get 10 upvotes or manually activate in admin)
2. Submit a prompt for the next chapter
3. In the admin panel, find the prompt and change its status to **"Winner"**
4. Watch the Celery worker terminal - you should see it processing the task
5. After ~30 seconds, a new chapter will be automatically created!

## Checking Task Status

You can monitor Celery tasks in the worker terminal. Look for:
```
[INFO] Task stories.tasks.generate_chapter_from_prompt[...] succeeded
```

## Troubleshooting

- **Redis not running**: Make sure Redis is started (`redis-cli ping` should return `PONG`)
- **Celery worker not picking up tasks**: Check that the worker is running and connected to Redis
- **OpenAI API errors**: Check your API key in `.env` file and ensure you have credits
