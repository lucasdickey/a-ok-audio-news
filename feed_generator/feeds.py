from django.contrib.syndication.views import Feed
from django.urls import reverse
from digests.models import DailyDigest
import json
from django.conf import settings
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import datetime # Import datetime

# Helper function to load podcast metadata from JSON file
def load_podcast_metadata(lang='en'):
    file_name = 'podcast.json' if lang == 'en' else 'podcast.zh.json'
    # Correctly join the base directory with the file name
    file_path = settings.BASE_DIR / file_name
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback or default metadata if file not found
        return {
            "title": "A-OK Podcast",
            "author": "A-OK",
            "owner": {"name": "A-OK", "email": "lucas@apesonkeys.com"},
            "description": "Podcast description.",
            "language": "en-us" if lang == 'en' else "zh-cn",
            "artwork_url": "",
            "category": "Technology",
            "explicit": False,
            "link": "https://www.a-ok.shop",
            "copyright": "© 2025 A-OK",
            "itunes_type": "episodic"
        }

class ExtendedPodcastFeed(Rss201rev2Feed):
    def rss_attributes(self):
        attrs = super().rss_attributes()
        attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        metadata = self.feed['metadata']
        handler.addQuickElement('itunes:author', metadata.get('author'))
        handler.addQuickElement('itunes:email', metadata.get('owner', {}).get('email'))
        handler.addQuickElement('itunes:explicit', 'yes' if metadata.get('explicit') else 'no')
        handler.addQuickElement('itunes:image', attrs={'href': metadata.get('artwork_url')})
        handler.addQuickElement('itunes:owner')
        handler.addQuickElement('itunes:name', metadata.get('owner', {}).get('name'))
        handler.addQuickElement('itunes:email', metadata.get('owner', {}).get('email'))
        handler.endElement('itunes:owner')
        handler.addQuickElement('itunes:category', text=metadata.get('category'))
        handler.addQuickElement('language', metadata.get('language'))
        handler.addQuickElement('copyright', metadata.get('copyright'))
        handler.addQuickElement('itunes:type', metadata.get('itunes_type', 'episodic'))


class BasePodcastFeed(Feed):
    feed_type = ExtendedPodcastFeed

    def __init__(self, lang_code='en'):
        self.lang_code = lang_code
        self.metadata = load_podcast_metadata(lang=self.lang_code)
        super().__init__()

    @property
    def title(self):
        return self.metadata.get('title')

    @property
    def link(self):
        # The link should be a valid URL. Using the base link from metadata.
        # Specific episode links will be handled by item_link.
        return self.metadata.get('link', '/#{self.lang_code}')


    @property
    def description(self):
        return self.metadata.get('description')

    def feed_extra_kwargs(self, obj):
        # Pass the whole metadata dict to the feed generator
        return {'metadata': self.metadata}

    def items(self):
        if self.lang_code == 'en':
            return DailyDigest.objects.filter(summary_text_en__isnull=False, audio_url_en__isnull=False).order_by('-date')[:50]
        else: # 'zh'
            return DailyDigest.objects.filter(summary_text_zh__isnull=False, audio_url_zh__isnull=False).order_by('-date')[:50]

    def item_title(self, item):
        return item.title_en if self.lang_code == 'en' else item.title_zh

    def item_description(self, item):
        return item.description_en if self.lang_code == 'en' else item.description_zh
    
    def item_link(self, item):
        # Each item should have a unique link.
        # This could be a link to a page for the episode, or just the audio file if no such page exists.
        # For now, let's point to the audio URL as a placeholder, but ideally this would be a permalink to an episode page.
        return item.audio_url_en if self.lang_code == 'en' else item.audio_url_zh

    def item_pubdate(self, item):
        # Combine date and a default time (e.g., midnight) if time is not stored
        return datetime.combine(item.date, datetime.min.time())

    def item_guid(self, item):
        # Use the audio URL as the GUID, or the item's ID if audio_url might change
        # For robustness, prefix with a domain or unique identifier
        audio_url = item.audio_url_en if self.lang_code == 'en' else item.audio_url_zh
        return audio_url or f"urn:uuid:{item.id}"

    def item_enclosure_url(self, item):
        return item.audio_url_en if self.lang_code == 'en' else item.audio_url_zh

    def item_enclosure_length(self, item):
        # This needs to be the size of the audio file in bytes.
        # This information isn't currently stored in DailyDigest.
        # For now, returning a placeholder. This should be updated.
        if self.lang_code == 'en':
            return str(item.audio_size_en) if item.audio_size_en else "0"
        else: # 'zh'
            return str(item.audio_size_zh) if item.audio_size_zh else "0"

    def item_enclosure_mime_type(self, item):
        # Assuming MP3 files. Adjust if other formats are used.
        return "audio/mpeg"

    # iTunes specific tags for the feed
    def feed_copyright(self):
        return self.metadata.get('copyright')

    def feed_language(self): # This method name is standard, maps to <language>
        return self.metadata.get('language')
    
    # author_name and author_email are for the <managingEditor> and <itunes:email> tags
    # The Feed class itself has 'author_name', 'author_email', 'author_link'.
    # We'll rely on the ExtendedPodcastFeed to handle itunes:author and itunes:email from metadata for the channel level

class EnPodcastFeed(BasePodcastFeed):
    def __init__(self):
        super().__init__(lang_code='en')

class ZhPodcastFeed(BasePodcastFeed):
    def __init__(self):
        super().__init__(lang_code='zh') 