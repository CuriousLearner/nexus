# Standard Library
import logging
import time
from functools import wraps

# Third Party Stuff
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor application performance"""

    @staticmethod
    def track_execution_time(func_name=None):
        """Decorator to track function execution time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log slow functions
                if execution_time > 1.0:  # More than 1 second
                    logger.warning(
                        f'Slow function: {func_name or func.__name__} '
                        f'took {execution_time:.2f}s'
                    )

                # Store metrics
                cache_key = f'perf:{func_name or func.__name__}:avg_time'
                avg_time = cache.get(cache_key, 0)
                # Simple moving average
                new_avg = (avg_time * 0.9) + (execution_time * 0.1)
                cache.set(cache_key, new_avg, 3600)

                return result
            return wrapper
        return decorator

    @staticmethod
    def track_database_queries():
        """Context manager to track database queries"""
        class QueryTracker:
            def __enter__(self):
                self.num_queries = len(connection.queries)
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.query_count = len(connection.queries) - self.num_queries
                self.duration = time.time() - self.start_time

                if self.query_count > 10:
                    logger.warning(
                        f'High query count: {self.query_count} queries '
                        f'in {self.duration:.2f}s'
                    )

        return QueryTracker()

    @staticmethod
    def get_metrics():
        """Get performance metrics"""
        return {
            'database': {
                'query_count': len(connection.queries),
                'queries': connection.queries[-10:] if settings.DEBUG else []
            },
            'cache': {
                'hits': cache.get('cache_hits', 0),
                'misses': cache.get('cache_misses', 0)
            }
        }


class ErrorTracker:
    """Track and log errors"""

    @staticmethod
    def log_error(error, context=None):
        """Log error with context"""
        logger.error(
            f'Error occurred: {str(error)}',
            exc_info=True,
            extra={'context': context or {}}
        )

        # Increment error counter
        error_type = error.__class__.__name__
        cache_key = f'errors:{error_type}:count'
        count = cache.get(cache_key, 0)
        cache.set(cache_key, count + 1, 3600)

    @staticmethod
    def track_exception(exc_type, exc_value, exc_traceback):
        """Track exception details"""
        import traceback

        error_info = {
            'type': exc_type.__name__,
            'message': str(exc_value),
            'traceback': ''.join(traceback.format_tb(exc_traceback)),
            'timestamp': timezone.now().isoformat()
        }

        logger.error('Exception tracked', extra=error_info)

        return error_info


class HealthCheck:
    """Application health check"""

    @staticmethod
    def check_database():
        """Check database connectivity"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True, "Database connection OK"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    @staticmethod
    def check_cache():
        """Check cache connectivity"""
        try:
            cache.set('health_check', True, 10)
            result = cache.get('health_check')
            cache.delete('health_check')
            if result:
                return True, "Cache connection OK"
            return False, "Cache read/write failed"
        except Exception as e:
            return False, f"Cache error: {str(e)}"

    @staticmethod
    def check_celery():
        """Check Celery worker status"""
        try:
            from nexus.celery import app
            inspector = app.control.inspect()
            active = inspector.active()
            if active:
                return True, f"Celery workers active: {len(active)}"
            return False, "No active Celery workers"
        except Exception as e:
            return False, f"Celery error: {str(e)}"

    @staticmethod
    def get_system_health():
        """Get overall system health"""
        checks = {
            'database': HealthCheck.check_database(),
            'cache': HealthCheck.check_cache(),
            'celery': HealthCheck.check_celery(),
        }

        all_healthy = all(status for status, _ in checks.values())

        return {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'checks': {
                name: {
                    'status': 'pass' if status else 'fail',
                    'message': message
                }
                for name, (status, message) in checks.items()
            },
            'timestamp': timezone.now().isoformat()
        }


class MetricsCollector:
    """Collect application metrics"""

    @staticmethod
    def increment_counter(metric_name, value=1, tags=None):
        """Increment a counter metric"""
        cache_key = f'metrics:counter:{metric_name}'
        if tags:
            cache_key += f':{":".join(f"{k}={v}" for k, v in tags.items())}'

        current = cache.get(cache_key, 0)
        cache.set(cache_key, current + value, 86400)  # 24 hours

    @staticmethod
    def record_gauge(metric_name, value, tags=None):
        """Record a gauge metric"""
        cache_key = f'metrics:gauge:{metric_name}'
        if tags:
            cache_key += f':{":".join(f"{k}={v}" for k, v in tags.items())}'

        cache.set(cache_key, value, 3600)

    @staticmethod
    def record_timing(metric_name, duration, tags=None):
        """Record timing metric"""
        cache_key = f'metrics:timing:{metric_name}'
        if tags:
            cache_key += f':{":".join(f"{k}={v}" for k, v in tags.items())}'

        # Store list of timings
        timings = cache.get(cache_key, [])
        timings.append(duration)
        # Keep last 100 measurements
        if len(timings) > 100:
            timings = timings[-100:]
        cache.set(cache_key, timings, 3600)

    @staticmethod
    def get_metrics():
        """Get all collected metrics"""
        # This would integrate with monitoring systems like Prometheus, Datadog, etc.
        return {
            'timestamp': timezone.now().isoformat(),
            'counters': {},  # Would fetch from cache
            'gauges': {},
            'timings': {}
        }


# Request tracking middleware

class RequestTrackingMiddleware:
    """Middleware to track request metrics"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track request start
        request.start_time = time.time()

        # Process request
        response = self.get_response(request)

        # Calculate duration
        duration = time.time() - request.start_time

        # Log slow requests
        if duration > 2.0:  # More than 2 seconds
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {duration:.2f}s'
            )

        # Record metrics
        MetricsCollector.increment_counter(
            'http_requests_total',
            tags={'method': request.method, 'status': response.status_code}
        )
        MetricsCollector.record_timing(
            'http_request_duration',
            duration,
            tags={'endpoint': request.path}
        )

        # Add timing header
        response['X-Response-Time'] = f'{duration:.3f}s'

        return response


# Logging configuration

def setup_logging():
    """Setup structured logging"""
    import logging.config

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{levelname}] {asctime} {name} {message}',
                'style': '{',
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/nexus.log',
                'maxBytes': 1024 * 1024 * 10,  # 10MB
                'backupCount': 5,
                'formatter': 'verbose'
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/errors.log',
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'formatter': 'json'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            'nexus': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }

    logging.config.dictConfig(LOGGING)


# Performance profiling

class Profiler:
    """Profile code execution"""

    def __init__(self, name='profile'):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        logger.info(
            f'Profile {self.name}: {duration:.4f}s',
            extra={'duration': duration, 'profile_name': self.name}
        )


# Alert system

class AlertManager:
    """Manage system alerts"""

    @staticmethod
    def send_alert(alert_type, message, severity='warning', metadata=None):
        """Send alert"""
        alert_data = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'metadata': metadata or {},
            'timestamp': timezone.now().isoformat()
        }

        # Log alert
        if severity == 'critical':
            logger.critical(f'ALERT: {message}', extra=alert_data)
        elif severity == 'error':
            logger.error(f'ALERT: {message}', extra=alert_data)
        else:
            logger.warning(f'ALERT: {message}', extra=alert_data)

        # Would integrate with alerting systems like PagerDuty, Slack, etc.

        return alert_data

    @staticmethod
    def check_thresholds():
        """Check metric thresholds and send alerts"""
        # Check error rate
        error_count = cache.get('errors:total:count', 0)
        if error_count > 100:
            AlertManager.send_alert(
                'high_error_rate',
                f'High error rate detected: {error_count} errors',
                severity='error'
            )

        # Check response time
        avg_response_time = cache.get('perf:avg_response_time', 0)
        if avg_response_time > 5.0:
            AlertManager.send_alert(
                'slow_response',
                f'Slow response time: {avg_response_time:.2f}s average',
                severity='warning'
            )
