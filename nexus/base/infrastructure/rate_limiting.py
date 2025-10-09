# Standard Library
from functools import wraps

# Third Party Stuff
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from rest_framework.throttling import SimpleRateThrottle


class RateLimiter:
    """Rate limiting utility"""

    def __init__(self, identifier, limit, window=60):
        """
        :param identifier: Unique identifier (IP, user ID, etc.)
        :param limit: Maximum requests allowed
        :param window: Time window in seconds
        """
        self.identifier = identifier
        self.limit = limit
        self.window = window
        self.cache_key = f'rate_limit:{identifier}'

    def is_allowed(self):
        """Check if request is allowed"""
        current = cache.get(self.cache_key, 0)
        return current < self.limit

    def increment(self):
        """Increment request counter"""
        current = cache.get(self.cache_key, 0)
        current += 1

        # Set with expiry if first request
        if current == 1:
            cache.set(self.cache_key, current, self.window)
        else:
            # Update without changing TTL
            cache.set(self.cache_key, current, cache.ttl(self.cache_key) or self.window)

        return current

    def get_remaining(self):
        """Get remaining requests"""
        current = cache.get(self.cache_key, 0)
        return max(0, self.limit - current)

    def get_reset_time(self):
        """Get time until reset"""
        return cache.ttl(self.cache_key) or 0

    def reset(self):
        """Reset counter"""
        cache.delete(self.cache_key)


def rate_limit(limit=100, window=60, key_func=None):
    """
    Rate limiting decorator for views

    Usage:
        @rate_limit(limit=10, window=60)
        def my_view(request):
            return Response({'data': 'success'})
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Determine identifier
            if key_func:
                identifier = key_func(request)
            else:
                # Default to IP address
                identifier = get_client_ip(request)

            # Check rate limit
            limiter = RateLimiter(identifier, limit, window)

            if not limiter.is_allowed():
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f'Maximum {limit} requests per {window} seconds',
                    'retry_after': limiter.get_reset_time()
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Increment counter
            limiter.increment()

            # Execute view
            response = view_func(request, *args, **kwargs)

            # Add rate limit headers
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = str(limit)
                response['X-RateLimit-Remaining'] = str(limiter.get_remaining())
                response['X-RateLimit-Reset'] = str(limiter.get_reset_time())

            return response

        return wrapper
    return decorator


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# DRF Throttle classes

class UserRateThrottle(SimpleRateThrottle):
    """Rate throttle per user"""
    scope = 'user'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class BurstRateThrottle(SimpleRateThrottle):
    """Short-term burst rate limiting"""
    scope = 'burst'
    rate = '60/min'


class SustainedRateThrottle(SimpleRateThrottle):
    """Long-term sustained rate limiting"""
    scope = 'sustained'
    rate = '1000/day'


class AnonRateThrottle(SimpleRateThrottle):
    """Rate throttle for anonymous users"""
    scope = 'anon'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return None  # Only throttle anonymous users

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class IPRateThrottle(SimpleRateThrottle):
    """Rate throttle by IP address"""
    scope = 'ip'

    def get_cache_key(self, request, view):
        ident = get_client_ip(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


# Advanced rate limiting patterns

class SlidingWindowRateLimiter:
    """Sliding window rate limiter for more accurate limiting"""

    def __init__(self, identifier, limit, window=60):
        self.identifier = identifier
        self.limit = limit
        self.window = window
        self.cache_key = f'sliding_rate_limit:{identifier}'

    def is_allowed(self, timestamp=None):
        """Check if request is allowed using sliding window"""
        import time
        if timestamp is None:
            timestamp = time.time()

        # Get request timestamps
        timestamps = cache.get(self.cache_key, [])

        # Remove old timestamps outside window
        cutoff = timestamp - self.window
        timestamps = [ts for ts in timestamps if ts > cutoff]

        # Check if under limit
        if len(timestamps) >= self.limit:
            return False

        # Add current timestamp
        timestamps.append(timestamp)
        cache.set(self.cache_key, timestamps, self.window)

        return True


class TokenBucketRateLimiter:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, identifier, capacity, refill_rate, refill_time=1):
        """
        :param identifier: Unique identifier
        :param capacity: Maximum tokens
        :param refill_rate: Tokens added per refill_time
        :param refill_time: Time between refills (seconds)
        """
        self.identifier = identifier
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_time = refill_time
        self.cache_key = f'token_bucket:{identifier}'

    def consume(self, tokens=1):
        """Try to consume tokens"""
        import time

        # Get current bucket state
        bucket = cache.get(self.cache_key)
        current_time = time.time()

        if bucket is None:
            # Initialize bucket
            bucket = {
                'tokens': self.capacity,
                'last_refill': current_time
            }

        # Refill tokens based on time passed
        time_passed = current_time - bucket['last_refill']
        refills = int(time_passed / self.refill_time)

        if refills > 0:
            bucket['tokens'] = min(
                self.capacity,
                bucket['tokens'] + (refills * self.refill_rate)
            )
            bucket['last_refill'] = current_time

        # Check if enough tokens
        if bucket['tokens'] >= tokens:
            bucket['tokens'] -= tokens
            cache.set(self.cache_key, bucket, self.refill_time * 100)
            return True

        return False


# Rate limiting middleware

class RateLimitMiddleware:
    """Middleware for global rate limiting"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Apply rate limiting
        ip = get_client_ip(request)
        limiter = RateLimiter(f'global:{ip}', limit=100, window=60)

        if not limiter.is_allowed():
            return JsonResponse({
                'error': 'Too many requests',
                'retry_after': limiter.get_reset_time()
            }, status=429)

        limiter.increment()

        response = self.get_response(request)

        # Add rate limit headers
        response['X-RateLimit-Limit'] = '100'
        response['X-RateLimit-Remaining'] = str(limiter.get_remaining())
        response['X-RateLimit-Reset'] = str(limiter.get_reset_time())

        return response


# API endpoint specific limiters

class EndpointRateLimiter:
    """Rate limiter for specific API endpoints"""

    LIMITS = {
        '/api/auth/login': (5, 300),  # 5 requests per 5 minutes
        '/api/auth/register': (3, 3600),  # 3 requests per hour
        '/api/posts': (100, 60),  # 100 requests per minute
        '/api/posts/create': (10, 60),  # 10 creates per minute
    }

    @classmethod
    def get_limit(cls, endpoint):
        """Get rate limit for endpoint"""
        for pattern, (limit, window) in cls.LIMITS.items():
            if endpoint.startswith(pattern):
                return limit, window
        return 100, 60  # Default limit

    @classmethod
    def check(cls, request):
        """Check rate limit for request"""
        endpoint = request.path
        limit, window = cls.get_limit(endpoint)

        identifier = f'{endpoint}:{get_client_ip(request)}'
        if request.user.is_authenticated:
            identifier = f'{endpoint}:user:{request.user.id}'

        limiter = RateLimiter(identifier, limit, window)
        return limiter.is_allowed()
