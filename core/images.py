import secrets
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def encode_webp(img, side, quality):
    """Encode a Pillow image as WebP, scaled down to fit a side x side box."""
    copy = img.copy()
    copy.thumbnail((side, side), Image.LANCZOS)
    buf = BytesIO()
    copy.save(buf, "WEBP", quality=quality, method=5)
    return ContentFile(buf.getvalue(), name=f"{secrets.token_hex(8)}.webp")


def optimize_upload(field_file, side, quality=82):
    """Turn a freshly uploaded image into a web-sized WebP, keeping any transparency."""
    img = ImageOps.exif_transpose(Image.open(field_file))
    return encode_webp(img.convert("RGBA" if img.has_transparency_data else "RGB"), side, quality)


def is_new_upload(field_file):
    return bool(field_file) and not field_file._committed
