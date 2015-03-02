from django import forms

from django.test import TestCase

from multifilefield.fields import MultiFileField
from multifilefield.mixins import MultiFileFieldMixin


# http://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django


class MultiFileFieldNoManagerTestCase(TestCase):
    def test_init(self):
        """Test that initializing the field doesn't break."""

        MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)

        self.assertTrue(True)


    def test_init_manager(self):
        """Test that initializing without manager."""

        MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)

        self.assertTrue(True)


    def test_init_manager_maximum(self):
        """Test that initializing without manager and max_num_total doesn't break."""

        MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0,
            max_num_total = 10)

        self.assertTrue(True)



class FormWithMultiFileFieldNoManagerTestCase(TestCase):
    """ This TestCase is for testing the form mixin. """


    def setUp(self):
        class TestFormNoManager(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                label='Uploads')

        self.TestFormNoManager = TestFormNoManager


    def test_init_no_manager(self):
        """Test that initializing the form doesn't break."""

        form = self.TestFormNoManager()
        self.assertTrue(True)
