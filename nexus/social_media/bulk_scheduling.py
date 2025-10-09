# Standard Library
import csv
import io
from datetime import datetime

# Third Party Stuff
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.social_media.models import Post


class BulkScheduleCSVProcessor:
    """Process CSV files for bulk post scheduling"""

    REQUIRED_FIELDS = ['text', 'scheduled_time']
    OPTIONAL_FIELDS = ['platforms', 'image_url', 'video_url', 'priority', 'is_draft']

    def __init__(self, csv_file, user):
        """
        Initialize processor

        :param csv_file: Uploaded CSV file
        :param user: User creating the posts
        """
        self.csv_file = csv_file
        self.user = user
        self.errors = []
        self.created_posts = []

    def validate_csv_format(self, reader):
        """Validate CSV has required columns"""
        try:
            headers = next(reader)
            headers = [h.strip().lower() for h in headers]

            # Check required fields
            for field in self.REQUIRED_FIELDS:
                if field not in headers:
                    raise ValidationError(f"Missing required column: {field}")

            return headers
        except StopIteration:
            raise ValidationError("CSV file is empty")

    def parse_datetime(self, datetime_str):
        """Parse datetime from various formats"""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(datetime_str.strip(), fmt)
                return timezone.make_aware(dt)
            except ValueError:
                continue

        raise ValidationError(f"Invalid datetime format: {datetime_str}")

    def parse_platforms(self, platforms_str):
        """Parse platforms from comma-separated string"""
        if not platforms_str:
            return []

        platforms = [p.strip().lower() for p in platforms_str.split(',')]
        valid_platforms = ['fb', 'twitter', 'linkedin', 'instagram', 'threads']

        # Validate platforms
        for platform in platforms:
            if platform not in valid_platforms:
                raise ValidationError(f"Invalid platform: {platform}")

        return platforms

    def process_row(self, row, headers, row_num):
        """Process a single CSV row"""
        try:
            # Create dict from row
            row_data = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_data[header] = row[i].strip()

            # Validate required fields
            if not row_data.get('text'):
                raise ValidationError("Text is required")

            if not row_data.get('scheduled_time'):
                raise ValidationError("Scheduled time is required")

            # Parse scheduled time
            scheduled_time = self.parse_datetime(row_data['scheduled_time'])

            # Parse platforms
            platforms = []
            posted_at = None

            if row_data.get('platforms'):
                platforms = self.parse_platforms(row_data['platforms'])
            elif row_data.get('posted_at'):
                # Legacy single platform support
                posted_at = row_data['posted_at'].lower()

            # Create post
            post = Post.objects.create(
                posted_by=self.user,
                text=row_data['text'],
                scheduled_time=scheduled_time,
                posted_at=posted_at,
                platforms=platforms,
                is_draft=row_data.get('is_draft', '').lower() in ['true', '1', 'yes'],
                is_approved=False,
            )

            # Create queue item if priority specified
            if row_data.get('priority'):
                from nexus.social_media.queue_models import PostQueue

                priority_map = {
                    'low': 'low',
                    'normal': 'normal',
                    'high': 'high',
                    'urgent': 'urgent'
                }

                priority = priority_map.get(row_data['priority'].lower(), 'normal')

                PostQueue.objects.create(
                    post=post,
                    priority=priority,
                    queue_position=PostQueue.objects.count()
                )

            self.created_posts.append(post)

            return {
                'success': True,
                'post_id': str(post.id),
                'text': post.text[:50]
            }

        except Exception as e:
            error_msg = f"Row {row_num}: {str(e)}"
            self.errors.append(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def process(self):
        """Process the entire CSV file"""
        try:
            # Decode file content
            content = self.csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Parse CSV
            csv_reader = csv.reader(io.StringIO(content))
            headers = self.validate_csv_format(csv_reader)

            results = []
            for row_num, row in enumerate(csv_reader, start=2):
                if not any(row):  # Skip empty rows
                    continue

                result = self.process_row(row, headers, row_num)
                results.append(result)

            return {
                'success': True,
                'total_rows': len(results),
                'created': len(self.created_posts),
                'errors': len(self.errors),
                'results': results,
                'error_messages': self.errors
            }

        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'created': len(self.created_posts),
                'errors': len(self.errors)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'created': len(self.created_posts),
                'errors': len(self.errors)
            }

    @staticmethod
    def generate_sample_csv():
        """Generate a sample CSV template"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        headers = ['text', 'scheduled_time', 'platforms', 'priority', 'is_draft']
        writer.writerow(headers)

        # Write sample rows
        writer.writerow([
            'Check out our latest blog post!',
            '2025-10-15 14:00:00',
            'fb,twitter,linkedin',
            'normal',
            'false'
        ])
        writer.writerow([
            'Join us for our upcoming webinar',
            '2025-10-16 10:00:00',
            'linkedin,twitter',
            'high',
            'false'
        ])
        writer.writerow([
            'New product launch announcement',
            '2025-10-17 09:00:00',
            'fb,instagram,threads',
            'urgent',
            'false'
        ])

        return output.getvalue()
