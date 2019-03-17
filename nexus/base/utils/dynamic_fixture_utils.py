# -*- coding: utf-8 -*-

# Standard Library
import random

# Third Party Stuff
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import SequentialDataFixture
# Nexus Stuff
from tests.utils import create_image


class PatchedSequentialDataFixture(SequentialDataFixture):
    """
    Patches default SequentialDataFixture to support PhoneNumberField.
    """

    def phonenumberfield_config(self, field, key):
        return '+1234560%s' % random.randint(1000, 9999)

    def durationfield_config(self, field, key):
        return '%s:%s:%s' % (
            random.randint(0, 24), random.randint(0, 59), random.randint(0, 59)
        )

    def jsonfield_config(self, field, key):
        return {}

    def filefield_config(self, field, key):
        f = File('/tmp/a')
        return f

    def versatileimagefield_config(self, field, key):
        image = create_image(None, 'image.png')
        image = SimpleUploadedFile('file.png', image.getvalue())
        return image
