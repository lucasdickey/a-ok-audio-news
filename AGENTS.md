---

## 🏗️ Data Model Guidance

### `DailyDigest` (core table)

| Field                     | Type        | Notes                          |
|--------------------------|-------------|--------------------------------|
| id                       | UUID        | PK                             |
| date                     | Date        | One per day                    |
| title_en                 | String      | Generated headline             |
| title_zh                 | String      | Translated title               |
| description_en           | Text        | SEO-heavy summary              |
| description_zh           | Text        | Mandarin summary               |
| keywords_en              | String      | Comma-separated                 |
| keywords_zh              | String      | Comma-separated                 |
| summary_text_en          | Text        | Full script (EN)               |
| summary_text_zh          | Text        | Full script (ZH)               |
| audio_url_en             | URL         | Vercel Blob link               |
| audio_url_zh             | URL         | Vercel Blob link               |
| gpt_prompt               | Text        | Input prompt for summary       |
| gpt_response_raw         | JSON        | Raw GPT return for auditing    |
| created_at               | DateTime    | Insert timestamp               |

---

## 🗂️ Static Show Metadata

### File: `podcast.json`

- Contains EN show-wide metadata (title, author, etc.)
- Used to generate base of `/rss.xml`

### File: `podcast.zh.json`

- Mandarin equivalent for `/rss-zh.xml`

Structure includes:

- Title
- Author + Owner Info
- Description
- Language (e.g., `en-us`, `zh-cn`)
- Artwork URL
- Category (`Technology`)
- Explicit flag

---

## 🪜 Logical Feature Branches (Chronological)

### `feature/initial-setup`

- Create Django project
- Configure Neon DB
- Define `DailyDigest` model
- Load podcast metadata from static JSON

---

### `feature/openai-summary`

- Call OpenAI with web-enabled prompt
- Get structured AI news summary for the day
- Store in `summary_text_en`

---

### `feature/metadata-generation`

- Prompt OpenAI to generate:
  - title_en
  - description_en
  - keywords_en

---

### `feature/tts-en`

- Send `summary_text_en` to ElevenLabs
- Save output to Vercel Blob
- Capture URL and audio length
- Store as `audio_url_en`

---

### `feature/translation-zh`

- Translate `summary_text_en` to Mandarin
- Store in `summary_text_zh`

---

### `feature/metadata-zh`

- Prompt OpenAI to generate:
  - title_zh
  - description_zh
  - keywords_zh

---

### `feature/tts-zh`

- Send `summary_text_zh` to ElevenLabs
- Use cloned Mandarin voice
- Save to Blob as `audio_url_zh`

---

### `feature/rss-en`

- Generate `/rss.xml`
- Uses `podcast.json` + all EN fields in `DailyDigest`
- Follows Apple/Spotify RSS podcast spec

---

### `feature/rss-zh`

- Generate `/rss-zh.xml`
- Uses `podcast.zh.json` + ZH fields in `DailyDigest`

---

### `feature/github-cron`

- GitHub Action YAML to:
  - Run `python manage.py run_daily_digest` daily
  - Inject secrets for API keys, DB, blob token
- Trigger: `"0 6 * * *"` UTC = 11PM PT

---

## 📁 Vercel Blob Folder Structure

/audio/en/YYYY/MM/DD/episode.mp3
/audio/zh/YYYY/MM/DD/episode.mp3
/transcripts/en/YYYY/MM/DD/script.txt
/transcripts/zh/YYYY/MM/DD/script.txt

---

## 🔄 Automation Summary

| Task                     | Automated? | Notes                         |
| ------------------------ | ---------- | ----------------------------- |
| AI summarization (EN)    | ✅         | OpenAI + system prompt        |
| Metadata generation (EN) | ✅         | Prompted from script          |
| Audio generation (EN)    | ✅         | ElevenLabs voice clone        |
| Translation to ZH        | ✅         | OpenAI translation prompt     |
| Metadata generation (ZH) | ✅         | Localized prompt              |
| Audio generation (ZH)    | ✅         | ElevenLabs (Mandarin voice)   |
| Blob uploads             | ✅         | Use Blob API programmatically |
| DB persistence           | ✅         | Django ORM into Neon          |
| RSS generation           | ✅         | Django view per language      |
| Cron job                 | ✅         | GitHub Actions daily run      |

---

## 🔐 Required Secrets (in GitHub)

- `OPENAI_API_KEY`
- `ELEVEN_API_KEY`
- `DATABASE_URL` (Neon)
- `VERCEL_BLOB_TOKEN`

---

## ✅ Completion Checklist

- [x] Podcast metadata files exist: `podcast.json`, `podcast.zh.json`
- [x] `/rss.xml` and `/rss-zh.xml` serve valid podcast feeds
- [ ] Audio + transcripts uploaded to Vercel Blob
- [ ] GitHub Action runs daily and logs output
- [ ] All fields in `DailyDigest` saved for each language
