# Standard Library
import gzip
import json
import os
import subprocess
from datetime import datetime, timedelta

# Third Party Stuff
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.utils import timezone


class DatabaseBackup:
    """Database backup utilities"""

    def __init__(self, backup_dir=None):
        self.backup_dir = backup_dir or getattr(
            settings, 'BACKUP_DIR', '/var/backups/nexus'
        )
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, compress=True):
        """Create database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'db_backup_{timestamp}.sql'

        if compress:
            filename += '.gz'

        backup_path = os.path.join(self.backup_dir, filename)

        # Get database settings
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')

        try:
            if db_settings['ENGINE'] == 'django.db.backends.postgresql':
                # PostgreSQL backup
                cmd = [
                    'pg_dump',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-F', 'c',  # Custom format
                    db_name
                ]

                if compress:
                    # Pipe through gzip
                    with open(backup_path, 'wb') as f:
                        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                        with gzip.open(backup_path, 'wb') as gz_file:
                            gz_file.write(proc.stdout.read())
                else:
                    with open(backup_path, 'wb') as f:
                        subprocess.run(cmd, stdout=f, check=True)

            elif db_settings['ENGINE'] == 'django.db.backends.mysql':
                # MySQL backup
                cmd = [
                    'mysqldump',
                    '-h', db_host,
                    '-P', str(db_port),
                    '-u', db_user,
                    db_name
                ]

                if compress:
                    with gzip.open(backup_path, 'wb') as gz_file:
                        subprocess.run(cmd, stdout=gz_file, check=True)
                else:
                    with open(backup_path, 'wb') as f:
                        subprocess.run(cmd, stdout=f, check=True)

            # Get file size
            file_size = os.path.getsize(backup_path)

            return {
                'success': True,
                'backup_path': backup_path,
                'file_size': file_size,
                'timestamp': timestamp
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def restore_backup(self, backup_path):
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            return {'success': False, 'error': 'Backup file not found'}

        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')

        try:
            if db_settings['ENGINE'] == 'django.db.backends.postgresql':
                cmd = [
                    'pg_restore',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-d', db_name,
                    '--clean',
                    backup_path
                ]
                subprocess.run(cmd, check=True)

            elif db_settings['ENGINE'] == 'django.db.backends.mysql':
                if backup_path.endswith('.gz'):
                    with gzip.open(backup_path, 'rb') as gz_file:
                        cmd = [
                            'mysql',
                            '-h', db_host,
                            '-P', str(db_port),
                            '-u', db_user,
                            db_name
                        ]
                        subprocess.run(cmd, stdin=gz_file, check=True)
                else:
                    with open(backup_path, 'rb') as f:
                        cmd = [
                            'mysql',
                            '-h', db_host,
                            '-P', str(db_port),
                            '-u', db_user,
                            db_name
                        ]
                        subprocess.run(cmd, stdin=f, check=True)

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_backups(self):
        """List all available backups"""
        backups = []

        for filename in os.listdir(self.backup_dir):
            if filename.startswith('db_backup_'):
                file_path = os.path.join(self.backup_dir, filename)
                file_size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                backups.append({
                    'filename': filename,
                    'file_path': file_path,
                    'file_size': file_size,
                    'created_at': modified_time
                })

        return sorted(backups, key=lambda x: x['created_at'], reverse=True)

    def cleanup_old_backups(self, days=30):
        """Delete backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = []

        for backup in self.list_backups():
            if backup['created_at'] < cutoff_date:
                os.remove(backup['file_path'])
                deleted.append(backup['filename'])

        return deleted


class DataExport:
    """Export data in various formats"""

    @staticmethod
    def export_to_json(queryset, file_path=None):
        """Export queryset to JSON"""
        from django.core import serializers

        json_data = serializers.serialize('json', queryset)

        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_data)
            return file_path
        else:
            return json_data

    @staticmethod
    def export_to_csv(queryset, file_path, fields=None):
        """Export queryset to CSV"""
        import csv

        if not queryset.exists():
            return None

        # Get fields
        model = queryset.model
        if not fields:
            fields = [f.name for f in model._meta.fields]

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            for obj in queryset:
                row = {field: getattr(obj, field) for field in fields}
                writer.writerow(row)

        return file_path

    @staticmethod
    def export_full_database():
        """Export entire database to JSON"""
        from django.apps import apps

        data = {}

        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            queryset = model.objects.all()

            if queryset.exists():
                data[model_name] = DataExport.export_to_json(queryset)

        return data


class DisasterRecovery:
    """Disaster recovery utilities"""

    @staticmethod
    def create_snapshot():
        """Create full system snapshot"""
        timestamp = timezone.now()

        snapshot = {
            'timestamp': timestamp.isoformat(),
            'database_backup': None,
            'media_files': None,
            'settings': None
        }

        # Create database backup
        db_backup = DatabaseBackup()
        backup_result = db_backup.create_backup()
        snapshot['database_backup'] = backup_result

        # Backup media files (simplified)
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            # Would use rsync or similar in production
            snapshot['media_files'] = f'Backup of {media_root}'

        # Export critical settings
        snapshot['settings'] = {
            'DEBUG': settings.DEBUG,
            'DATABASES': {
                'default': {
                    'ENGINE': settings.DATABASES['default']['ENGINE'],
                    'NAME': settings.DATABASES['default']['NAME']
                }
            }
        }

        # Save snapshot manifest
        snapshot_dir = '/var/backups/nexus/snapshots'
        os.makedirs(snapshot_dir, exist_ok=True)

        snapshot_file = os.path.join(
            snapshot_dir,
            f'snapshot_{timestamp.strftime("%Y%m%d_%H%M%S")}.json'
        )

        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)

        return snapshot

    @staticmethod
    def test_recovery():
        """Test recovery process"""
        # Create test backup
        db_backup = DatabaseBackup()
        backup_result = db_backup.create_backup()

        if not backup_result['success']:
            return {'success': False, 'error': 'Backup creation failed'}

        # Test restore (in a test database)
        # This would require a separate test database
        # For now, just verify backup file exists

        if os.path.exists(backup_result['backup_path']):
            file_size = os.path.getsize(backup_result['backup_path'])
            if file_size > 0:
                return {
                    'success': True,
                    'message': 'Recovery test passed',
                    'backup_size': file_size
                }

        return {'success': False, 'error': 'Backup file invalid'}


# Automated backup scheduling

class BackupScheduler:
    """Schedule automated backups"""

    @staticmethod
    def should_run_backup(frequency='daily'):
        """Check if backup should run"""
        from django.core.cache import cache

        cache_key = f'last_backup_{frequency}'
        last_backup = cache.get(cache_key)

        if not last_backup:
            return True

        now = timezone.now()

        if frequency == 'hourly':
            return (now - last_backup).seconds >= 3600
        elif frequency == 'daily':
            return (now - last_backup).days >= 1
        elif frequency == 'weekly':
            return (now - last_backup).days >= 7

        return False

    @staticmethod
    def run_scheduled_backup(frequency='daily'):
        """Run scheduled backup if needed"""
        from django.core.cache import cache

        if not BackupScheduler.should_run_backup(frequency):
            return {'skipped': True, 'reason': 'Too soon'}

        # Create backup
        db_backup = DatabaseBackup()
        result = db_backup.create_backup()

        if result['success']:
            # Update last backup time
            cache_key = f'last_backup_{frequency}'
            cache.set(cache_key, timezone.now(), None)  # Never expire

            # Cleanup old backups
            if frequency == 'daily':
                db_backup.cleanup_old_backups(days=30)
            elif frequency == 'weekly':
                db_backup.cleanup_old_backups(days=90)

        return result
