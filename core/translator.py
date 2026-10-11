"""Draft machine translation for the admin. DeepL Free if a key is set, MyMemory otherwise."""

import logging

import requests
from django.conf import settings

log = logging.getLogger(__name__)

DEEPL_CODES = {"en": "EN-GB", "ru": "RU", "tr": "TR"}
MYMEMORY_CHUNK = 450  # MyMemory rejects queries over 500 bytes


class TranslationError(Exception):
    pass


def translate_many(texts, source, target):
    """Translate a list of strings; empty strings stay empty."""
    if source == target:
        return list(texts)
    if settings.DEEPL_API_KEY:
        return _deepl(texts, source, target)
    return [_mymemory(t, source, target) if t.strip() else t for t in texts]


def provider_name():
    return "DeepL" if settings.DEEPL_API_KEY else "MyMemory"


def _deepl(texts, source, target):
    key = settings.DEEPL_API_KEY
    host = "api-free.deepl.com" if key.endswith(":fx") else "api.deepl.com"
    indexed = [(i, t) for i, t in enumerate(texts) if t.strip()]
    result = list(texts)
    if not indexed:
        return result
    try:
        resp = requests.post(
            f"https://{host}/v2/translate",
            headers={"Authorization": f"DeepL-Auth-Key {key}"},
            json={
                "text": [t for _, t in indexed],
                "source_lang": source.upper(),
                "target_lang": DEEPL_CODES[target],
                "preserve_formatting": True,
            },
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("DeepL failed: %s", exc)
        raise TranslationError(f"DeepL: {exc}") from exc
    for (i, _), item in zip(indexed, resp.json()["translations"]):
        result[i] = item["text"]
    return result


def _mymemory(text, source, target):
    out = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            out.append(paragraph)
            continue
        out.append(" ".join(_mymemory_chunk(c, source, target) for c in _chunks(paragraph)))
    return "\n".join(out)


def _chunks(text):
    words, buf = text.split(" "), ""
    for word in words:
        candidate = f"{buf} {word}".strip()
        if len(candidate.encode()) > MYMEMORY_CHUNK and buf:
            yield buf
            buf = word
        else:
            buf = candidate
    if buf:
        yield buf


def _mymemory_chunk(chunk, source, target):
    try:
        resp = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": chunk, "langpair": f"{source}|{target}"},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise TranslationError(f"MyMemory: {exc}") from exc
    if data.get("responseStatus") != 200:
        raise TranslationError(f"MyMemory: {data.get('responseDetails')}")
    return data["responseData"]["translatedText"]
