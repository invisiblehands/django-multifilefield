from datetime import datetime
from django import forms
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from multifilefield.fields import MultiFileField, NoFileFieldNameException
from multifilefield.mixins import MultiFileFieldMixin
from multifilefield.models import UploadedFile
from multifilefield.tests import *



class MultiFileFieldQuerySetTestCase(TestCase):
    """ Let's test that the queryset is working properly in
    populating the uploaded files."""


    def setUp(self):
        make_files()
        self.queryset = UploadedFile.objects.all()
        self.storage = TestStorage()


    def test_init(self):
        """Test that initializing the field doesn't break."""

        MultiFileField(
            add_label='Attach files',
            clear_label='Clear files',
            storage = self.storage,
            queryset = self.queryset,
            filefield_name='upload',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)

        self.assertTrue(True)


    def test_made_files(self):
        self.assertEqual(UploadedFile.objects.count(), 6)


    def test_no_filefield_name(self):
        """Test that queryset requires filefield_name"""

        self.assertRaises(NoFileFieldNameException, MultiFileField, queryset = self.queryset)


    def test_with_filefield_name(self):
        """Test that queryset requires filefield_name"""

        MultiFileField(
            queryset = self.queryset,
            filefield_name='upload')

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
        self.queryset = UploadedFile.objects.all()
        self.storage = TestStorage()

        class TestFormWithQueryset(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                storage = self.storage,
                queryset = self.queryset,
                filefield_name='upload')

        self.TestFormWithQueryset = TestFormWithQueryset
        self.factory = RequestFactory()


    def test_with_queryset(self):
        """Test form with a request."""

        data = {}
        request = self.factory.post('/fake/', data=data)
        form = self.TestFormWithQueryset(request.POST, request.FILES)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data
            self.assertEqual(len(cleaned_data.get('uploads')), 6)
        else:
            self.fail(form.errors)


    def test_with_queryset_clear(self):
        """Test form with a request.  Clear four files."""

        data = {'uploads_1': ('1', '2', '3', '4')}
        request = self.factory.post('/fake/', data=data)
        form = self.TestFormWithQueryset(request.POST, request.FILES)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data
            self.assertEqual(len(cleaned_data.get('uploads')), 2)
        else:
            self.fail(form.errors)


    def test_with_queryset_upload_new_file(self):
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


    def test_with_queryset_upload_new_file_clear_four(self):
        """Test form with a request.  Add new file and clear four files."""

        upload = SimpleUploadedFile('uploaded_file.jpeg',
            'file_content', content_type='image/jpeg')

        data = {
            'uploads_0': upload,
            'uploads_1': ('1', '2', '3', '4')
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
