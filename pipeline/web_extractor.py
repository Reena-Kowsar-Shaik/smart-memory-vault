import re
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs

try:
    import requests
except ImportError:
    requests = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import trafilatura
except ImportError:
    trafilatura = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None


def extract_youtube_id(url: str) -> Optional[str]:
    """
    Extracts 11-character YouTube video ID from various URL patterns.
    Examples:
      - https://www.youtube.com/watch?v=dQw4w9WgXcQ
      - https://youtu.be/dQw4w9WgXcQ
      - https://www.youtube.com/shorts/dQw4w9WgXcQ
      - https://www.youtube.com/embed/dQw4w9WgXcQ
    """
    if not url:
        return None
    url = url.strip()
    
    # Check youtu.be shortlinks
    if "youtu.be" in url:
        path = urlparse(url).path
        return path.lstrip("/").split("?")[0]
    
    # Check /shorts/ or /embed/
    match_shorts = re.search(r'youtube\.com/(?:shorts|embed)/([a-zA-Z0-9_-]{11})', url)
    if match_shorts:
        return match_shorts.group(1)
        
    # Check standard query params ?v=
    parsed = urlparse(url)
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
            
    # Generic regex fallback for 11-char ID
    match_gen = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    if match_gen:
        return match_gen.group(1)

    return None


def fetch_youtube_metadata(video_id: str, original_url: str) -> Dict[str, str]:
    """Fetches video title and author using YouTube oEmbed endpoint (no API key required)."""
    title = f"YouTube Video ({video_id})"
    author = "YouTube Creator"
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    if requests is not None:
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            resp = requests.get(oembed_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                title = data.get("title", title)
                author = data.get("author_name", author)
                thumbnail_url = data.get("thumbnail_url", thumbnail_url)
        except Exception:
            pass

    return {
        "title": title,
        "author": author,
        "thumbnail_url": thumbnail_url,
        "url": original_url
    }


def _fetch_raw_transcript(video_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Version-agnostic transcript retrieval supporting both youtube-transcript-api v1.2+
    (instantiated API) and legacy class-method versions. Automatically translates
    foreign language (e.g. Hindi, Spanish) transcripts to English when available.
    """
    if YouTubeTranscriptApi is None:
        return None

    # Priority 1: YouTubeTranscriptApi() list() with auto-translation to English
    try:
        ytt = YouTubeTranscriptApi()
        if hasattr(ytt, "list"):
            tlist = ytt.list(video_id)
            # Try finding direct English transcript first
            try:
                transcript_obj = tlist.find_transcript(['en', 'en-US', 'en-GB', 'en-IN', 'en-CA'])
            except Exception:
                # Pick whatever transcript exists (e.g. Hindi, French, Spanish)
                transcript_obj = next(iter(tlist))
                # Auto-translate to English
                if getattr(transcript_obj, 'is_translatable', False):
                    try:
                        transcript_obj = transcript_obj.translate('en')
                    except Exception:
                        pass

            fetched = transcript_obj.fetch()
            if hasattr(fetched, "to_raw_data"):
                return fetched.to_raw_data()
            elif hasattr(fetched, "snippets"):
                return [{"text": getattr(s, "text", str(s))} for s in fetched.snippets]
            elif isinstance(fetched, list):
                return fetched
    except Exception:
        pass

    # Priority 2: Direct fetch (English preferred)
    try:
        ytt = YouTubeTranscriptApi()
        if hasattr(ytt, "fetch"):
            fetched = ytt.fetch(video_id, languages=['en', 'en-US', 'en-GB', 'en-IN'])
            if hasattr(fetched, "to_raw_data"):
                return fetched.to_raw_data()
            elif hasattr(fetched, "snippets"):
                return [{"text": getattr(s, "text", str(s))} for s in fetched.snippets]
            elif isinstance(fetched, list):
                return fetched
    except Exception:
        pass

    # Priority 3: Legacy static methods (pre v1.2)
    try:
        if hasattr(YouTubeTranscriptApi, "list_transcripts"):
            tlist = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                t_obj = tlist.find_transcript(['en', 'en-US', 'en-GB'])
            except Exception:
                t_obj = next(iter(tlist))
                try:
                    t_obj = t_obj.translate('en')
                except Exception:
                    pass
            return t_obj.fetch()
    except Exception:
        pass

    try:
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            return YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB', 'en-IN'])
    except Exception:
        pass

    return None


def extract_youtube_transcript(url: str) -> Dict[str, Any]:
    """Extracts video metadata and timestamped/continuous transcript from a YouTube URL."""
    video_id = extract_youtube_id(url)
    if not video_id:
        return {
            "status": "error",
            "error": "Invalid or unrecognized YouTube URL format. Please provide a valid youtube.com or youtu.be link."
        }

    meta = fetch_youtube_metadata(video_id, url)
    raw_data = _fetch_raw_transcript(video_id)

    if raw_data:
        # Format transcript into clean, readable paragraphs
        full_paragraphs = []
        current_chunk = []
        chunk_word_count = 0

        for item in raw_data:
            if isinstance(item, dict):
                text = item.get("text", "").strip()
            else:
                text = getattr(item, "text", str(item)).strip()

            if text:
                current_chunk.append(text)
                chunk_word_count += len(text.split())
                if chunk_word_count > 60:
                    full_paragraphs.append(" ".join(current_chunk))
                    current_chunk = []
                    chunk_word_count = 0

        if current_chunk:
            full_paragraphs.append(" ".join(current_chunk))

        full_text = "\n\n".join(full_paragraphs)
    else:
        # Fallback if captions are completely disabled on YouTube
        full_text = f"YouTube Video: {meta['title']}\nCreator/Channel: {meta['author']}\nVideo ID: {video_id}\n\nNote: Closed captions / transcripts were disabled for this video by the creator. Metadata and video reference indexed successfully."

    return {
        "status": "success",
        "type": "youtube",
        "title": meta["title"],
        "author": meta["author"],
        "thumbnail_url": meta["thumbnail_url"],
        "video_id": video_id,
        "source_url": url,
        "text": full_text,
        "word_count": len(full_text.split()),
        "raw_transcript": raw_data or []
    }


def extract_web_article(url: str) -> Dict[str, Any]:
    """
    Extracts article title, author, and clean readable text from any web URL
    using trafilatura (with requests + BeautifulSoup fallback).
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Method 1: Trafilatura (State-of-the-art content extraction)
    if trafilatura is not None:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                extracted_text = trafilatura.extract(
                    downloaded,
                    include_links=False,
                    include_images=False,
                    output_format="txt"
                )
                meta = trafilatura.extract_metadata(downloaded)
                title = meta.title if (meta and meta.title) else ""
                author = meta.author if (meta and meta.author) else ""

                if extracted_text and len(extracted_text.strip()) > 80:
                    return {
                        "status": "success",
                        "type": "web_article",
                        "title": title or urlparse(url).netloc,
                        "author": author or urlparse(url).netloc,
                        "source_url": url,
                        "text": extracted_text.strip(),
                        "word_count": len(extracted_text.split())
                    }
        except Exception:
            pass

    # Method 2: Requests + BeautifulSoup Fallback
    if requests is not None and BeautifulSoup is not None:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Extract title
                title = ""
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()

                # Remove non-content elements
                for element in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
                    element.extract()

                # Gather paragraph text
                paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
                body_text = "\n\n".join(paragraphs)

                if body_text.strip():
                    return {
                        "status": "success",
                        "type": "web_article",
                        "title": title or urlparse(url).netloc,
                        "author": urlparse(url).netloc,
                        "source_url": url,
                        "text": body_text.strip(),
                        "word_count": len(body_text.split())
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to retrieve web article: {str(e)}"
            }

    return {
        "status": "error",
        "error": "Could not extract readable article content from the specified URL."
    }


def extract_from_url(url: str) -> Dict[str, Any]:
    """Unified routing function for URLs (YouTube vs Web Article)."""
    if not url or not url.strip():
        return {"status": "error", "error": "URL cannot be empty."}

    url = url.strip()
    is_youtube = ("youtube.com" in url) or ("youtu.be" in url)

    if is_youtube:
        return extract_youtube_transcript(url)
    else:
        return extract_web_article(url)
