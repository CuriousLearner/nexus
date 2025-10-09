# Standard Library
import hashlib
import json
from functools import wraps

# Third Party Stuff
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT


def cache_key(*args, **kwargs):
    """Generate cache key from arguments"""
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(timeout=DEFAULT_TIMEOUT, key_prefix='', version=None):
    """
    Decorator to cache function results

    Usage:
        @cached(timeout=300, key_prefix='user_posts')
        def get_user_posts(user_id):
            return Post.objects.filter(user_id=user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_args = f'{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}'

            # Try to get from cache
            result = cache.get(cache_key_args, version=version)

            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key_args, result, timeout, version=version)

            return result

        # Add cache invalidation method
        def invalidate(*args, **kwargs):
            cache_key_args = f'{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}'
            cache.delete(cache_key_args, version=version)

        wrapper.invalidate = invalidate

        return wrapper
    return decorator


def cache_model_instance(model_class, timeout=3600):
    """
    Cache model instance by ID

    Usage:
        user = cache_model_instance(User, timeout=600)(user_id)
    """
    def get_instance(pk):
        cache_key_str = f'model:{model_class.__name__}:{pk}'

        # Try cache first
        instance = cache.get(cache_key_str)
        if instance is not None:
            return instance

        # Get from database
        try:
            instance = model_class.objects.get(pk=pk)
            cache.set(cache_key_str, instance, timeout)
            return instance
        except model_class.DoesNotExist:
            return None

    return get_instance


def invalidate_model_cache(model_instance):
    """Invalidate cache for a model instance"""
    cache_key_str = f'model:{model_instance.__class__.__name__}:{model_instance.pk}'
    cache.delete(cache_key_str)


def cache_queryset(queryset, timeout=300, key_prefix='queryset'):
    """Cache queryset results"""
    # Generate unique key based on query
    query_hash = hashlib.md5(str(queryset.query).encode()).hexdigest()
    cache_key_str = f'{key_prefix}:{query_hash}'

    # Try cache
    result = cache.get(cache_key_str)
    if result is not None:
        return result

    # Execute query
    result = list(queryset)

    # Cache results
    cache.set(cache_key_str, result, timeout)

    return result


class CacheManager:
    """Centralized cache management"""

    @staticmethod
    def get_stats():
        """Get cache statistics"""
        # This would depend on cache backend
        # For Redis, you could use INFO command
        return {
            'backend': cache.__class__.__name__,
            'location': getattr(cache, '_server', 'N/A'),
        }

    @staticmethod
    def clear_pattern(pattern):
        """Clear cache keys matching pattern (Redis only)"""
        try:
            from django.core.cache.backends.redis import RedisCache
            if isinstance(cache, RedisCache):
                keys = cache.client.keys(pattern)
                if keys:
                    cache.client.delete(*keys)
                return len(keys)
        except ImportError:
            pass
        return 0

    @staticmethod
    def warm_cache(data_dict, timeout=3600):
        """Warm cache with multiple keys"""
        cache.set_many(data_dict, timeout)

    @staticmethod
    def get_or_set_many(keys, default_func, timeout=3600):
        """Get multiple keys or set if missing"""
        result = cache.get_many(keys)
        missing_keys = set(keys) - set(result.keys())

        if missing_keys:
            new_data = {key: default_func(key) for key in missing_keys}
            cache.set_many(new_data, timeout)
            result.update(new_data)

        return result


# Common cache patterns

def cache_user_permissions(user_id, timeout=1800):
    """Cache user permissions"""
    cache_key_str = f'user_permissions:{user_id}'

    permissions = cache.get(cache_key_str)
    if permissions is not None:
        return permissions

    # Get permissions from database
    from nexus.users.models import User
    try:
        user = User.objects.get(id=user_id)
        permissions = list(user.get_all_permissions())
        cache.set(cache_key_str, permissions, timeout)
        return permissions
    except User.DoesNotExist:
        return []


def cache_api_response(view_func):
    """Cache API view responses"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Only cache GET requests
        if request.method != 'GET':
            return view_func(request, *args, **kwargs)

        # Generate cache key from request
        cache_key_str = f'api:{request.path}:{cache_key(request.GET.dict())}'

        # Check cache
        response = cache.get(cache_key_str)
        if response is not None:
            return response

        # Execute view
        response = view_func(request, *args, **kwargs)

        # Cache successful responses
        if hasattr(response, 'status_code') and response.status_code == 200:
            cache.set(cache_key_str, response, 300)  # 5 minutes

        return response

    return wrapper


# Session cache helpers

def cache_session_data(session_key, data, timeout=3600):
    """Cache session-specific data"""
    cache_key_str = f'session:{session_key}:data'
    cache.set(cache_key_str, data, timeout)


def get_cached_session_data(session_key):
    """Get cached session data"""
    cache_key_str = f'session:{session_key}:data'
    return cache.get(cache_key_str)


# Rate limiting cache

def increment_rate_limit(identifier, window=60):
    """Increment rate limit counter"""
    cache_key_str = f'rate_limit:{identifier}'
    count = cache.get(cache_key_str, 0)
    count += 1
    cache.set(cache_key_str, count, window)
    return count


def check_rate_limit(identifier, limit, window=60):
    """Check if rate limit exceeded"""
    cache_key_str = f'rate_limit:{identifier}'
    count = cache.get(cache_key_str, 0)
    return count >= limit
