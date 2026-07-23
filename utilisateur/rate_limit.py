import time
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse


def rate_limit(key_prefix, max_attempts=5, window=300):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            ip = request.META.get("REMOTE_ADDR", "unknown")
            cache_key = f"ratelimit:{key_prefix}:{ip}"
            attempts = cache.get(cache_key, 0)

            if attempts >= max_attempts:
                return HttpResponse(
                    "<h1>Trop de tentatives.</h1>"
                    "<p>Veuillez réessayer dans quelques minutes.</p>",
                    status=429,
                    content_type="text/html",
                )

            response = view_func(request, *args, **kwargs)

            if request.method == "POST":
                cache.set(cache_key, attempts + 1, window)

            return response
        return _wrapped
    return decorator
