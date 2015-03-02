from django import forms

from django.test import TestCase

from multifilefield.fields import MultiFileField
from multifilefield.mixins import MultiFileFieldMixin


class MultiFileFieldTestCase(TestCase):
    def test_init(self):
        """Test that initializing the field doesn't break."""

        MultiFileField(
            add_label='Attach files',
            remove_label='Clear files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)

        self.assertTrue(True)


    def test_init_maximum(self):
        """Test that initializing and max_num_total doesn't break."""

        MultiFileField(
            add_label='Attach files',
            remove_label='Clear files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0,
            max_num_total = 10)

        self.assertTrue(True)



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
