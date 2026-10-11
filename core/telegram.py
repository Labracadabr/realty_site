import logging
import threading
from html import escape

import requests
from django.conf import settings

log = logging.getLogger(__name__)


def _send(chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
            timeout=10,
        ).raise_for_status()
    except requests.RequestException as exc:
        log.warning("Telegram notify to %s failed: %s", chat_id, exc)


def notify_lead(lead):
    if not settings.TELEGRAM_BOT_TOKEN:
        log.info("Telegram disabled (no token); lead #%s saved", lead.pk)
        return
    chats = {settings.TELEGRAM_CHAT_ID} if settings.TELEGRAM_CHAT_ID else set()
    for user in (lead.referrer, lead.property.responsible if lead.property else None):
        if user and user.telegram_chat_id:
            chats.add(user.telegram_chat_id)
    if not chats:
        return

    lines = ["🌴 <b>New lead</b>"]
    if lead.property:
        lines.append(f"🏝 {escape(lead.property.ref)} · {escape(lead.property.title_en or lead.property.title)}")
    lines.append(f"👤 {escape(lead.name)}")
    for icon, value in (("✉️", lead.email), ("📞", lead.phone), ("✈️", lead.telegram)):
        if value:
            lines.append(f"{icon} {escape(value)}")
    if lead.interest:
        lines.append(f"🎯 {escape(lead.interest)}")
    if lead.message:
        lines.append(f"\n{escape(lead.message[:1500])}")
    meta = [f"lang: {lead.language}"]
    if lead.referrer:
        meta.append(f"via: {escape(str(lead.referrer))}")
    if lead.share_link and lead.share_link.label:
        meta.append(f"link: {escape(lead.share_link.label)}")
    if lead.utm.get("utm_source"):
        meta.append(f"utm: {escape(lead.utm.get('utm_source'))}/{escape(lead.utm.get('utm_campaign', ''))}")
    lines.append("\n<i>" + " · ".join(meta) + "</i>")
    lines.append(f"{settings.SITE_URL}/{settings.ADMIN_URL}listings/lead/{lead.pk}/change/")

    text = "\n".join(lines)
    for chat in chats:
        threading.Thread(target=_send, args=(chat, text), daemon=True).start()
