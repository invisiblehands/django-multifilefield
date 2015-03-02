from django import forms

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import Storage
from django.test import TestCase

from multifilefield.fields import MultiFileField
from multifilefield.mixins import MultiFileFieldMixin
from multifilefield.models import UploadedFile


# http://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django


class MultiFileFieldManagerTestCase(TestCase):
    """ Let's test that the manager is working properly in
    populating the uploaded files."""

    # fixtures = ['images']

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

        self.assertTrue(True)



class FormWithMultiFileFieldManagerTestCase(TestCase):
    """ This TestCase is for testing the form mixin. """

    # fixtures = ['images']


    def setUp(self):
        """ setup the class we're gonna use for testing.  I did it
        this way to avoid the class being initialized before
        django test runner has setup the tests database with the appropriate
        tables for querying.  The uploadedfiles table is queried
        during initialization of the form."""

        class TestFormWithManager(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                label='Uploads',
                manager = UploadedFile.objects)

        self.TestFormWithManager = TestFormWithManager


    def test_init_with_manager(self):
        """Test that initializing the form doesn't break."""

        form = self.TestFormWithManager()

        print form.as_p()

        self.assertTrue(True)
