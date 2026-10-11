import json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .translator import TranslationError, provider_name, translate_many

LANG_CODES = {code for code, _ in settings.LANGUAGES}
MAX_CHARS = 30_000


@staff_member_required
@require_POST
def translate_fields(request):
    """POST {source, targets: [..], fields: {name: text}} -> {translations: {lang: {name: text}}}"""
    try:
        payload = json.loads(request.body)
        source = payload["source"]
        targets = [t for t in payload["targets"] if t in LANG_CODES and t != source]
        fields = {str(k): str(v) for k, v in payload["fields"].items()}
    except (ValueError, KeyError, TypeError, AttributeError):
        return JsonResponse({"error": "Bad request"}, status=400)
    if source not in LANG_CODES or not targets or not fields:
        return JsonResponse({"error": "Nothing to translate"}, status=400)
    if sum(len(v) for v in fields.values()) > MAX_CHARS:
        return JsonResponse({"error": f"Text too long (>{MAX_CHARS} chars)"}, status=400)

    names, texts = list(fields), list(fields.values())
    result = {}
    try:
        for target in targets:
            result[target] = dict(zip(names, translate_many(texts, source, target)))
    except TranslationError as exc:
        return JsonResponse({"error": str(exc), "partial": result}, status=502)
    return JsonResponse({"translations": result, "provider": provider_name()})
