from django import forms

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import Storage
from django.test import TestCase

from multifilefield.fields import MultiFileField
from multifilefield.mixins import MultiFileFieldMixin
from multifilefield.models import UploadedFile


# http://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django


class MultiFileFieldTest(TestCase):
    def test_init(self):
        """Test that initializing the field doesn't break."""

        uploads = MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            manager = UploadedFile.objects,
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)


    def test_init_manager(self):
        """Test that initializing with manager."""

        uploads = MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            manager = UploadedFile.objects,
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)


    def test_init_manager_maximum(self):
        """Test that initializing with manager and max_num_total doesn't break."""

        uploads = MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            manager = UploadedFile.objects,
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0,
            max_num_total = 10)



class FormWithMultiFileFieldTest(TestCase):
    """ This TestCase is for testing the form mixin. """

    def setUp(self):
        class TestFormNoManager(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                label='Uploads')


        class TestFormWithManager(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                label='Uploads',
                manager = UploadedFile.objects)

        self.TestFormNoManager = TestFormNoManager
        self.TestFormWithManager = TestFormWithManager


    def test_init_no_manager(self):
        """Test that initializing the form doesn't break."""

        form = self.TestFormNoManager()

        print form.as_p()


    def test_init_with_manager(self):
        """Test that initializing the form doesn't break."""

        form = self.TestFormWithManager()

        print form.as_p()
