# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class PostTemplate(TimeStampedUUIDModel):
    """Model for reusable post templates"""

    name = models.CharField(_('Template Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                   related_name='post_templates', verbose_name=_('Created By'))

    # Content
    text_template = models.TextField(
        _('Text Template'),
        help_text='Use {{variable_name}} for placeholders'
    )
    image = models.ImageField(_('Default Image'), upload_to='post_templates/', null=True, blank=True)
    video = models.FileField(_('Default Video'), upload_to='post_template_videos/', null=True, blank=True)

    # Platform defaults
    default_platforms = models.JSONField(
        _('Default Platforms'),
        default=list,
        blank=True,
        help_text='Default platforms to post to'
    )

    # Usage tracking
    times_used = models.PositiveIntegerField(_('Times Used'), default=0)
    last_used_at = models.DateTimeField(_('Last Used At'), null=True, blank=True)

    # Categorization
    category = models.CharField(_('Category'), max_length=100, blank=True,
                               help_text='e.g., Announcement, Promotion, Update')
    tags = models.JSONField(_('Tags'), default=list, blank=True)

    # Sharing
    is_public = models.BooleanField(_('Is Public'), default=False,
                                   help_text='Allow other users to use this template')

    class Meta:
        verbose_name = _('Post Template')
        verbose_name_plural = _('Post Templates')
        db_table = 'post_templates'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def render(self, context=None):
        """Render template with given context

        :param context: Dict of variable names and values
        :returns: Rendered text
        """
        if not context:
            context = {}

        text = self.text_template
        for key, value in context.items():
            placeholder = f'{{{{{key}}}}}'
            text = text.replace(placeholder, str(value))

        return text

    def create_post_from_template(self, user, context=None, **kwargs):
        """Create a Post instance from this template

        :param user: User creating the post
        :param context: Dict for template variables
        :param kwargs: Additional fields for the Post
        :returns: Created Post instance
        """
        from django.utils import timezone
        from nexus.social_media.models import Post

        rendered_text = self.render(context)

        post_data = {
            'posted_by': user,
            'text': rendered_text,
            'platforms': self.default_platforms,
        }

        # Override with any provided kwargs
        post_data.update(kwargs)

        post = Post.objects.create(**post_data)

        # Copy template image/video if not provided
        if self.image and not post.image:
            post.image = self.image
            post.save()

        if self.video and not post.video:
            post.video = self.video
            post.save()

        # Update usage stats
        self.times_used += 1
        self.last_used_at = timezone.now()
        self.save()

        return post


class TemplateVariable(TimeStampedUUIDModel):
    """Model to define variables for templates"""

    template = models.ForeignKey(PostTemplate, on_delete=models.CASCADE,
                                related_name='variables', verbose_name=_('Template'))
    name = models.CharField(_('Variable Name'), max_length=100,
                           help_text='Variable name without curly braces')
    description = models.TextField(_('Description'), blank=True,
                                  help_text='What this variable represents')
    default_value = models.TextField(_('Default Value'), blank=True)
    is_required = models.BooleanField(_('Is Required'), default=False)

    class Meta:
        verbose_name = _('Template Variable')
        verbose_name_plural = _('Template Variables')
        db_table = 'template_variables'
        unique_together = [['template', 'name']]
        ordering = ['template', 'name']

    def __str__(self):
        return f'{self.template.name} - {self.name}'
