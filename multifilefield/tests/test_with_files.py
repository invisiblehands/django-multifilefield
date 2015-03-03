from datetime import datetime
from django import forms
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from multifilefield.fields import MultiFileField, NoFileFieldNameException
from multifilefield.mixins import MultiFileFieldMixin
from multifilefield.models import UploadedFile
from multifilefield.tests import *



class MultiFileFieldFilesTestCase(TestCase):
    """ Let's test that the files is working properly in
    populating the uploaded files."""


    def setUp(self):
        make_files()
        self.files = get_files()
        self.storage = TestStorage()


    def test_init(self):
        """Test that initializing the field doesn't break."""

        MultiFileField(
            storage = self.storage,
            files = self.files)

        self.assertTrue(True)


    def tearDown(self):
        remove_files()



class FormWithMultiFileFieldQuerySetTestCase(TestCase):
    """ This TestCase is for testing the form mixin. """


    def setUp(self):
        """ setup the class we're gonna use for testing.  I did it
        this way to avoid the class being initialized before
        django test runner has setup the tests database with the appropriate
        tables for querying.  The uploadedfiles table is queried
        during initialization of the form."""

        make_files()
        self.files = get_files()
        self.storage = TestStorage()

        class TestFormWithQueryset(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                storage = self.storage,
                files = self.files)

        self.TestFormWithQueryset = TestFormWithQueryset
        self.factory = RequestFactory()


    def test_with_files(self):
        """Test form with a request."""

        data = {}
        request = self.factory.post('/fake/', data=data)
        form = self.TestFormWithQueryset(request.POST)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data
            self.assertEqual(len(cleaned_data.get('uploads')), 6)
        else:
            self.fail(form.errors)


    def test_with_files_clear(self):
        """Test form with a request.  Clear four files."""

        data = {'uploads_1': ('image_1.jpeg', 'image_2.jpeg', 'image_3.jpeg', 'image_4.jpeg',)}
        request = self.factory.post('/fake/', data=data)
        form = self.TestFormWithQueryset(request.POST)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data
            self.assertEqual(len(cleaned_data.get('uploads')), 2)
        else:
            self.fail(form.errors)


    def test_with_files_upload_new_file(self):
        """Test form with a request.  Add new file."""

        upload = SimpleUploadedFile('uploaded_file.jpeg',
            'file_content', content_type='image/jpeg')

        data = {'uploads_0': upload}
        request = self.factory.post('/fake/', data=data)
        form = self.TestFormWithQueryset(request.POST, request.FILES)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data
            self.assertEqual(len(cleaned_data.get('uploads')), 7)
        else:
            self.fail(form.errors)


    def test_with_files_upload_new_file_clear_four(self):
        """Test form with a request.  Add new file and clear four files."""

        upload = SimpleUploadedFile('uploaded_file.jpeg',
            'file_content', content_type='image/jpeg')

        data = {
            'uploads_0': upload,
            'uploads_1': ('image_1.jpeg', 'image_2.jpeg', 'image_3.jpeg', 'image_4.jpeg',)
        }

        request = self.factory.post('/fake/', data=data)
        form = self.TestFormWithQueryset(request.POST, request.FILES)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data
            self.assertEqual(len(cleaned_data.get('uploads')), 3)
        else:
            self.fail(form.errors)


    def tearDown(self):
        remove_files()
