import re
from decimal import Decimal

from django import template
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def usd(value):
    if value in (None, ""):
        return ""
    return f"${Decimal(value):,.0f}"


@register.filter
def num(value, decimals=0):
    """1234567.5 -> 1,234,567.5 (trailing zeros dropped)."""
    if value in (None, ""):
        return ""
    value = Decimal(value)
    text = f"{value:,.{int(decimals)}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@register.filter
def absolute(url):
    return url if url.startswith("http") else settings.SITE_URL + url


_BOLD = re.compile(r"\*\*(.+?)\*\*")


def _inline(text):
    return _BOLD.sub(r"<strong>\1</strong>", escape(text))


@register.filter
def richtext(text):
    """Tiny safe markup: blank line = paragraph, '## ' heading, '- ' list, **bold**."""
    if not text:
        return ""
    html = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if lines[0].startswith("## "):
            html.append(f"<h2>{_inline(lines[0][3:])}</h2>")
            lines = lines[1:]
            if not lines:
                continue
        if all(line.lstrip().startswith(("- ", "• ")) for line in lines):
            items = "".join(f"<li>{_inline(line.lstrip()[2:])}</li>" for line in lines)
            html.append(f"<ul>{items}</ul>")
        else:
            html.append("<p>" + "<br>".join(_inline(line) for line in lines) + "</p>")
    return mark_safe("\n".join(html))


@register.inclusion_tag("partials/icon.html")
def icon(name, size=20):
    return {"name": name, "size": size}


@register.simple_tag(takes_context=True)
def lead_initial(context, field):
    request = context.get("request")
    data = request.session.get("lead_form_data", {}) if request else {}
    return data.get(field, "")
