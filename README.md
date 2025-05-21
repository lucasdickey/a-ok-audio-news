# A-OK Audio News

A-OK Audio News is a Django-based application that creates short AI-generated news digests as a podcast. The project automatically summarizes AI news, generates metadata, produces audio in English and Mandarin, and publishes both RSS feeds and transcripts.

## Features

The repository is organized around a series of logical feature branches that build up the automation pipeline:

1. **Initial Setup** – Django project creation, Neon database configuration, `DailyDigest` model definition, and loading static podcast metadata.
2. **OpenAI Summary** – Daily web-enabled prompt for news summarization stored in `summary_text_en`.
3. **Metadata Generation** – AI-generated titles, descriptions, and keywords for the English episode.
4. **English Text-to-Speech** – ElevenLabs voice synthesis for the English script, uploaded to Vercel Blob storage.
5. **Translation to Mandarin** – Translation of the summary text and creation of the Mandarin script.
6. **Mandarin Metadata and TTS** – Localized metadata and audio generation using a Mandarin voice clone.
7. **RSS Feeds** – Generation of `/rss.xml` and `/rss-zh.xml` using `podcast.json` and `podcast.zh.json`.
8. **GitHub Cron Job** – Daily automation with GitHub Actions to run the digest.

## Data Model

The core table is `DailyDigest`, which stores both English and Mandarin episode data:

| Field            | Type   | Notes                            |
| ---------------- | ------ | -------------------------------- |
| `id`             | UUID   | Primary key                      |
| `date`           | Date   | One entry per day                |
| `title_en`       | String | Generated English headline       |
| `title_zh`       | String | Translated Mandarin headline     |
| `description_en` | Text   | SEO-friendly summary             |
| `description_zh` | Text   | Mandarin summary                 |
| `keywords_en`    | String | Comma-separated keywords         |
| `keywords_zh`    | String | Comma-separated keywords         |
| `summary_text_en`| Text   | Full English script              |
| `summary_text_zh`| Text   | Full Mandarin script             |
| `audio_url_en`   | URL    | Link to English audio file       |
| `audio_url_zh`   | URL    | Link to Mandarin audio file      |
| `gpt_prompt`     | Text   | Input prompt for OpenAI          |
| `gpt_response_raw`| JSON  | Raw OpenAI response              |
| `created_at`     | DateTime | Timestamp of creation          |

Static show-wide metadata is stored in `podcast.json` and `podcast.zh.json`. These files provide information such as the podcast title, author, description, language, artwork URL, and more.

## Folder Structure for Vercel Blob Storage

```
/audio/en/YYYY/MM/DD/episode.mp3
/audio/zh/YYYY/MM/DD/episode.mp3
/transcripts/en/YYYY/MM/DD/script.txt
/transcripts/zh/YYYY/MM/DD/script.txt
```

## Required Secrets

The GitHub Actions workflow expects the following secrets:

- `OPENAI_API_KEY`
- `ELEVEN_API_KEY`
- `DATABASE_URL`
- `VERCEL_BLOB_TOKEN`

## Completion Checklist

- [ ] `podcast.json` and `podcast.zh.json` exist
- [ ] Valid `/rss.xml` and `/rss-zh.xml` feeds are generated
- [ ] Audio and transcripts uploaded to Vercel Blob
- [ ] GitHub Action runs daily and logs output
- [ ] All fields in `DailyDigest` are saved for each language

