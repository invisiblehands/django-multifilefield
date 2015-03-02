from django import forms

from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from multifilefield.fields import MultiFileField
from multifilefield.mixins import MultiFileFieldMixin


class MultiFileFieldTestCase(TestCase):
    def test_init(self):
        """Test field doesn't break during initialization."""


        upload = SimpleUploadedFile('/long/path/uploaded_file.jpeg',
            'file_content', content_type='image/jpeg')


        MultiFileField(
            add_label='Attach files',
            clear_label='Clear files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)

        self.assertTrue(True)


    def test_required(self):
        """Test field required validation functions properly."""

        field = MultiFileField(required=False)
        field.validate(None)
        field.validate([None, None])
        field.validate([[], []])

        field = MultiFileField(required=True)
        self.assertRaises(ValidationError, field.validate, None)
        self.assertRaises(ValidationError, field.validate, [None, None])
        self.assertRaises(ValidationError, field.validate, [[], []])

        upload = SimpleUploadedFile('uploaded_file.jpeg',
            'file_content', content_type='image/jpeg')

        field.validate([upload, None])
        field.validate([[upload], None])
        field.validate([[upload], []])



class FormWithMultiFileFieldTestCase(TestCase):
    """ This TestCase is for testing the form mixin. """


    def setUp(self):
        class TestForm(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField()

        self.TestForm = TestForm


    def test_init(self):
        """Test that initializing the form doesn't break."""

        form = self.TestForm()
        self.assertTrue(True)
