# Standard Library
import logging

# Third Party Stuff
from django.db import connection, models
from django.db.models import Prefetch

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def analyze_query(queryset):
        """Analyze queryset and suggest optimizations"""
        suggestions = []

        # Check for select_related opportunities
        if hasattr(queryset, 'query'):
            # Analyze foreign keys
            model = queryset.model
            for field in model._meta.get_fields():
                if isinstance(field, models.ForeignKey):
                    suggestions.append(
                        f"Consider using select_related('{field.name}') for {field.name}"
                    )

            # Analyze many-to-many
            for field in model._meta.get_fields():
                if isinstance(field, models.ManyToManyField):
                    suggestions.append(
                        f"Consider using prefetch_related('{field.name}') for {field.name}"
                    )

        return suggestions

    @staticmethod
    def log_queries(func):
        """Decorator to log SQL queries executed by function"""
        def wrapper(*args, **kwargs):
            from django.conf import settings
            if not settings.DEBUG:
                return func(*args, **kwargs)

            # Reset queries
            connection.queries_log.clear()

            result = func(*args, **kwargs)

            # Log queries
            num_queries = len(connection.queries)
            if num_queries > 10:
                logger.warning(
                    f'{func.__name__} executed {num_queries} queries',
                    extra={
                        'function': func.__name__,
                        'query_count': num_queries,
                        'queries': connection.queries
                    }
                )

            return result

        return wrapper

    @staticmethod
    def get_query_stats():
        """Get query statistics"""
        if not connection.queries:
            return {}

        total_time = sum(float(q['time']) for q in connection.queries)
        return {
            'total_queries': len(connection.queries),
            'total_time': total_time,
            'avg_time': total_time / len(connection.queries) if connection.queries else 0,
            'slowest_query': max(connection.queries, key=lambda q: float(q['time'])) if connection.queries else None
        }


class BulkOperations:
    """Optimized bulk database operations"""

    @staticmethod
    def bulk_create_optimized(model_class, objects, batch_size=1000):
        """Bulk create with optimized batch size"""
        created = []
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            created.extend(model_class.objects.bulk_create(batch, batch_size=batch_size))

        logger.info(f'Bulk created {len(created)} {model_class.__name__} objects')
        return created

    @staticmethod
    def bulk_update_optimized(objects, fields, batch_size=1000):
        """Bulk update with optimized batch size"""
        from django.db.models import Model

        if not objects:
            return 0

        model_class = objects[0].__class__
        updated = 0

        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            updated += model_class.objects.bulk_update(batch, fields, batch_size=batch_size)

        logger.info(f'Bulk updated {updated} {model_class.__name__} objects')
        return updated

    @staticmethod
    def chunked_queryset(queryset, chunk_size=1000):
        """Iterate queryset in chunks to avoid memory issues"""
        pk = 0
        while True:
            chunk = queryset.filter(pk__gt=pk)[:chunk_size]
            if not chunk:
                break

            for obj in chunk:
                yield obj
                pk = obj.pk


class IndexOptimization:
    """Database index optimization"""

    @staticmethod
    def suggest_indexes(model_class):
        """Suggest missing indexes for a model"""
        suggestions = []

        # Check foreign keys without db_index
        for field in model_class._meta.get_fields():
            if isinstance(field, models.ForeignKey) and not field.db_index:
                suggestions.append(f"Add db_index=True to {field.name}")

        # Check fields commonly used in filters
        # This would require query log analysis in production

        return suggestions

    @staticmethod
    def find_duplicate_indexes():
        """Find duplicate database indexes"""
        # This would query information_schema to find redundant indexes
        with connection.cursor() as cursor:
            # PostgreSQL specific query
            cursor.execute("""
                SELECT tablename, indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """)
            indexes = cursor.fetchall()

        # Analyze for duplicates
        # This is a simplified version
        return indexes


class ConnectionPooling:
    """Database connection pool management"""

    @staticmethod
    def get_pool_stats():
        """Get connection pool statistics"""
        # This depends on the database backend and connection pooling library
        return {
            'active_connections': 0,  # Would get from pool
            'idle_connections': 0,
            'max_connections': 0,
        }

    @staticmethod
    def close_old_connections():
        """Close old database connections"""
        from django.db import close_old_connections
        close_old_connections()


# Query result caching

class QueryResultCache:
    """Cache query results"""

    @staticmethod
    def cache_queryset(cache_key, queryset, timeout=300):
        """Cache queryset results"""
        from django.core.cache import cache

        # Convert queryset to list and cache
        results = list(queryset)
        cache.set(cache_key, results, timeout)
        return results

    @staticmethod
    def get_cached_queryset(cache_key):
        """Get cached queryset results"""
        from django.core.cache import cache
        return cache.get(cache_key)


# Database-specific optimizations

class PostgreSQLOptimizations:
    """PostgreSQL-specific optimizations"""

    @staticmethod
    def analyze_table(table_name):
        """Run ANALYZE on a table"""
        with connection.cursor() as cursor:
            cursor.execute(f"ANALYZE {table_name};")

    @staticmethod
    def vacuum_table(table_name, full=False):
        """Run VACUUM on a table"""
        with connection.cursor() as cursor:
            if full:
                cursor.execute(f"VACUUM FULL {table_name};")
            else:
                cursor.execute(f"VACUUM {table_name};")

    @staticmethod
    def get_table_stats(table_name):
        """Get table statistics"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    pg_size_pretty(pg_total_relation_size('{table_name}')) AS total_size,
                    pg_size_pretty(pg_relation_size('{table_name}')) AS table_size,
                    pg_size_pretty(pg_indexes_size('{table_name}')) AS indexes_size,
                    n_live_tup AS live_tuples,
                    n_dead_tup AS dead_tuples
                FROM pg_stat_user_tables
                WHERE relname = '{table_name}';
            """)
            return cursor.fetchone()

    @staticmethod
    def get_slow_queries(limit=10):
        """Get slow queries from pg_stat_statements"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT {limit};
            """)
            return cursor.fetchall()


# N+1 query detection

class NPlusOneDetector:
    """Detect N+1 query problems"""

    def __init__(self):
        self.query_count_before = 0
        self.queries_before = []

    def __enter__(self):
        self.query_count_before = len(connection.queries)
        self.queries_before = list(connection.queries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        queries_after = connection.queries[self.query_count_before:]
        query_count = len(queries_after)

        if query_count > 10:
            # Analyze for N+1 patterns
            similar_queries = {}
            for query in queries_after:
                # Normalize query (remove specific IDs)
                normalized = query['sql']
                for digit in '0123456789':
                    normalized = normalized.replace(digit, 'X')

                if normalized not in similar_queries:
                    similar_queries[normalized] = 0
                similar_queries[normalized] += 1

            # Find repeated queries
            repeated = {q: count for q, count in similar_queries.items() if count > 5}

            if repeated:
                logger.warning(
                    'Possible N+1 query detected',
                    extra={
                        'total_queries': query_count,
                        'repeated_queries': repeated
                    }
                )


# Prefetch optimization helpers

def optimize_prefetch(queryset, *relations):
    """Helper to optimize prefetch_related"""
    prefetch_objects = []

    for relation in relations:
        if isinstance(relation, str):
            prefetch_objects.append(Prefetch(relation))
        elif isinstance(relation, dict):
            # Allow custom queryset
            relation_name = relation['relation']
            queryset_func = relation.get('queryset')
            if queryset_func:
                prefetch_objects.append(
                    Prefetch(relation_name, queryset=queryset_func())
                )
            else:
                prefetch_objects.append(Prefetch(relation_name))

    return queryset.prefetch_related(*prefetch_objects)


# Database migration helpers

class MigrationOptimizer:
    """Optimize database migrations"""

    @staticmethod
    def create_index_concurrently(model_name, index_name, columns):
        """Create index without locking table (PostgreSQL)"""
        from django.db import migrations

        return migrations.RunSQL(
            sql=f"CREATE INDEX CONCURRENTLY {index_name} ON {model_name} ({', '.join(columns)});",
            reverse_sql=f"DROP INDEX CONCURRENTLY IF EXISTS {index_name};"
        )

    @staticmethod
    def add_column_with_default(table_name, column_name, column_type, default_value):
        """Add column with default without full table rewrite"""
        # PostgreSQL 11+ optimization
        return [
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};",
            f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT {default_value};",
        ]
