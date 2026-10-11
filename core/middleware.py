UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid")


class UTMMiddleware:
    """Remember the first ad/campaign parameters of a visit for lead attribution."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        params = {k: request.GET[k][:200] for k in UTM_KEYS if k in request.GET}
        if params and "utm" not in request.session:
            request.session["utm"] = params
        return self.get_response(request)
