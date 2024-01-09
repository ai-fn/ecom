class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(".")
        if len(host) > 2:
            request.subdomain = host[0]
        else:
            request.subdomain = None

        return self.get_response(request)
