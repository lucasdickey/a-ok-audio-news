# A-OK Audio News

A-OK Audio News is a Django-based application that creates short AI-generated news digests as a podcast. The project automatically summarizes AI news, generates metadata, produces audio in English and Mandarin, and publishes both RSS feeds and transcripts.

## Features

The repository is organized around a series of logical feature branches that build up the automation pipeline:

1. **Initial Setup** – Django project creation, Supabase database configuration, `DailyDigest` model definition, and loading static podcast metadata.
2. **OpenAI Summary** – Daily web-enabled prompt for news summarization stored in `summary_text_en`.
3. **Metadata Generation** – AI-generated titles, descriptions, and keywords for the English episode.
4. **English Text-to-Speech** – ElevenLabs voice synthesis for the English script, uploaded to Vercel Blob storage.
5. **Translation to Mandarin** – Translation of the summary text and creation of the Mandarin script.
6. **Mandarin Metadata and TTS** – Localized metadata and audio generation using a Mandarin voice clone.
7. **RSS Feeds** – Generation of `/rss.xml` and `/rss-zh.xml` using `podcast.json` and `podcast.zh.json`.
8. **GitHub Cron Job** – Daily automation with GitHub Actions to run the digest.

## Data Model

The core table is `DailyDigest`, which stores both English and Mandarin episode data:

| Field              | Type     | Notes                        |
| ------------------ | -------- | ---------------------------- |
| `id`               | UUID     | Primary key                  |
| `date`             | Date     | One entry per day            |
| `title_en`         | String   | Generated English headline   |
| `title_zh`         | String   | Translated Mandarin headline |
| `description_en`   | Text     | SEO-friendly summary         |
| `description_zh`   | Text     | Mandarin summary             |
| `keywords_en`      | String   | Comma-separated keywords     |
| `keywords_zh`      | String   | Comma-separated keywords     |
| `summary_text_en`  | Text     | Full English script          |
| `summary_text_zh`  | Text     | Full Mandarin script         |
| `audio_url_en`     | URL      | Link to English audio file   |
| `audio_url_zh`     | URL      | Link to Mandarin audio file  |
| `llm_prompt`       | Text     | Input prompt for LLM         |
| `llm_response_raw` | JSON     | Raw LLM response             |
| `created_at`       | DateTime | Timestamp of creation        |

Static show-wide metadata is stored in `podcast.json` and `podcast.zh.json`. These files provide information such as the podcast title, author, description, language, artwork URL, and more.

## Folder Structure for Vercel Blob Storage

```
/audio/en/YYYY/MM/DD/episode.mp3
/audio/zh/YYYY/MM/DD/episode.mp3
/transcripts/en/YYYY/MM/DD/script.txt
/transcripts/zh/YYYY/MM/DD/script.txt
```

## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd a-ok-audio-news
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    _(On Windows, use `venv\Scripts\activate`)_
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    _(Ensure you have a `requirements.txt` file. If not, you can generate one after installing dependencies manually: `pip freeze > requirements.txt`)_
4.  **Set up environment variables:**
    Create a `.env.local` file in the project root and add your API keys and database URL. See the "Required Secrets" section for the necessary variables.
    Example `.env.local`:
    ```
    OPENAI_API_KEY="sk-..."
    ELEVEN_API_KEY="..."
    DATABASE_URL="postgresql://user:password@host:port/dbname"
    VERCEL_BLOB_TOKEN="..."
    ANTHROPIC_API_KEY="sk-..."
    ```
5.  **Run database migrations:**
    ```bash
    venv/bin/python manage.py makemigrations
    venv/bin/python manage.py migrate
    ```

## Required Secrets

The GitHub Actions workflow expects the following secrets:

- `OPENAI_API_KEY`
- `ELEVEN_API_KEY`
- `DATABASE_URL`
- `VERCEL_BLOB_TOKEN`

## Completion Checklist

- [x] `podcast.json` and `podcast.zh.json` exist
- [x] Valid `/rss.xml` and `/rss-zh.xml` feeds are generated
- [ ] Audio and transcripts uploaded to Vercel Blob
- [ ] GitHub Action runs daily and logs output
- [ ] All fields in `DailyDigest` are saved for each language

## API Endpoints

All endpoints are prefixed with `/api/`.

### DailyDigest CRUD

- `GET    /api/digests/` — List all digests
- `POST   /api/digests/` — Create a new digest
- `GET    /api/digests/{id}/` — Retrieve a digest by UUID
- `PUT    /api/digests/{id}/` — Update a digest
- `PATCH  /api/digests/{id}/` — Partial update
- `DELETE /api/digests/{id}/` — Delete a digest

### Text-to-Speech (TTS)

- `POST /api/tts/`
  - Request: `{ "text": "...", "lang": "en", "voice": "default" }`
  - Response: `{ "audio_url": "..." }`

### Publish Audio & Metadata to RSS

- `POST /api/publish/`
  - Request: `{ "audio_url": "...", "title": "...", "description": "...", "date": "YYYY-MM-DD", "lang": "en", "keywords": "...", "transcript_url": "..." }`
  - Response: `{ "rss_url": "...", "status": "published" }`

## Running Tests

To run the available tests for the Django application (e.g., for the `digests` app):

```bash
venv/bin/python manage.py test digests
```

Make sure your virtual environment is activated and your database is configured correctly, as tests might interact with the database.
