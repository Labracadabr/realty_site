import re
from urllib.parse import parse_qs, urlparse

_YT_ID = re.compile(r"^[\w-]{11}$")


def video_embed_url(url):
    """Turn a YouTube / Vimeo page link into a privacy-friendly embed URL."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    video_id = None
    if host == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
    elif host in ("youtube.com", "youtube-nocookie.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        else:
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2 and parts[0] in ("embed", "shorts", "live"):
                video_id = parts[1]
    if video_id and _YT_ID.match(video_id):
        return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"
    if host in ("vimeo.com", "player.vimeo.com"):
        digits = [p for p in parsed.path.split("/") if p.isdigit()]
        if digits:
            return f"https://player.vimeo.com/video/{digits[0]}"
    return None
