def client_ip(request):
    """Real visitor IP behind our nginx (used by django-axes for login lockouts).

    nginx sets X-Forwarded-For with $proxy_add_x_forwarded_for, which appends the address it
    actually saw as the last item, so the last entry can't be spoofed by the client.
    Without the header (local runserver) fall back to REMOTE_ADDR.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")
