from django import forms

from django.core.exceptions import ValidationError
from django.test import TestCase

from multifilefield import ClearableFilesField



class ClearableFilesFieldTest(TestCase):
    def test_init(self):
        """Test that initializing the field doesn't break."""

        clearable_files_field = ClearableFilesField(
            label='Upload files',
            required=False)

        #self.assertEqual()
