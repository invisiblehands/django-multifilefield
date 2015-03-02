from datetime import datetime
from django import forms

from django.test import TestCase

from multifilefield.fields import MultiFileField, NoFileFieldNameException
from multifilefield.mixins import MultiFileFieldMixin
from multifilefield.models import UploadedFile


# http://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django


class MultiFileFieldManagerTestCase(TestCase):
    """ Let's test that the manager is working properly in
    populating the uploaded files."""

    fixtures = ['images']


    def test_init(self):
        """Test that initializing the field doesn't break."""

        MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            manager = UploadedFile.objects,
            filefield_name='upload',
            required = False,
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)

        self.assertTrue(True)


    def test_no_filefield_name(self):
        """Test that manager also requires filefield_name"""

        self.assertRaises(NoFileFieldNameException, MultiFileField, manager = UploadedFile.objects)


    def test_with_filefield_name(self):
        """Test that manager also requires filefield_name"""

        MultiFileField(
            manager = UploadedFile.objects,
            filefield_name='upload')

        self.assertTrue(True)


    def test_fixtures(self):
        self.assertEqual(UploadedFile.objects.count(), 6)



class FormWithMultiFileFieldManagerTestCase(TestCase):
    """ This TestCase is for testing the form mixin. """

    fixtures = ['images']


    def setUp(self):
        """ setup the class we're gonna use for testing.  I did it
        this way to avoid the class being initialized before
        django test runner has setup the tests database with the appropriate
        tables for querying.  The uploadedfiles table is queried
        during initialization of the form."""

        class TestFormWithManager(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                label='Uploads',
                manager = UploadedFile.objects,
                filefield_name='upload')

        self.TestFormWithManager = TestFormWithManager


    def test_init_with_manager(self):
        """Test that initializing the form doesn't break."""

        form = self.TestFormWithManager()

        self.assertTrue(True)
