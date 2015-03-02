import os, shutil, tempfile

from datetime import datetime
from django import forms
from django.test.utils import override_settings
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile

from multifilefield.fields import MultiFileField, NoFileFieldNameException
from multifilefield.mixins import MultiFileFieldMixin
from multifilefield.models import UploadedFile


TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')
TEMP_FILES_DIR = tempfile.mkdtemp(dir=os.path.dirname(__file__))


def make_files():
    if not os.access(TEMP_FILES_DIR, os.F_OK):
        os.makedirs(TEMP_FILES_DIR)


    for filename in os.listdir(TEST_FILES_DIR):
        src = os.path.join(TEST_FILES_DIR, filename)
        dest = os.path.join(TEMP_FILES_DIR, filename)
        shutil.copyfile(src, dest)


    tmp_files = [os.path.join(TEMP_FILES_DIR, filename) for filename in os.listdir(TEMP_FILES_DIR)]
    bulk = [UploadedFile(upload=tmp_file) for tmp_file in tmp_files]
    UploadedFile.objects.bulk_create(bulk)


def remove_files():
    shutil.rmtree(TEMP_FILES_DIR)



@override_settings(MULTIFILEFIELD_ROOT=TEMP_FILES_DIR)
@override_settings(MULTIFILEFIELD_URL='files')
class MultiFileFieldManagerTestCase(TestCase):
    """ Let's test that the manager is working properly in
    populating the uploaded files."""


    def setUp(self):
        make_files()


    def test_init(self):
        """Test that initializing the field doesn't break."""

        MultiFileField(
            label ='Uploads',
            add_label='Attach files',
            remove_label='Clear files',
            manager = UploadedFile.objects,
            filefield_name='upload',
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


    def tearDown(self):
        remove_files()



@override_settings(MULTIFILEFIELD_ROOT=TEMP_FILES_DIR)
@override_settings(MULTIFILEFIELD_URL='files')
class FormWithMultiFileFieldManagerTestCase(TestCase):
    """ This TestCase is for testing the form mixin. """


    def setUp(self):
        """ setup the class we're gonna use for testing.  I did it
        this way to avoid the class being initialized before
        django test runner has setup the tests database with the appropriate
        tables for querying.  The uploadedfiles table is queried
        during initialization of the form."""

        make_files()


        class TestFormWithManager(MultiFileFieldMixin, forms.Form):
            uploads = MultiFileField(
                label='Uploads',
                manager = UploadedFile.objects,
                filefield_name='upload')

            class Meta:
                process_files_for=['uploads']


        self.TestFormWithManager = TestFormWithManager
        self.factory = RequestFactory()


    def test_init_with_manager_upload_new_file(self):
        """Test initialization of the form with a request."""

        pth = '/fake/pth/'
        upload = SimpleUploadedFile('uploaded_file.jpeg',
            'file_content', content_type='image/jpeg')

        data = {
            'uploads_0': upload,
            'uploads_1': ('1', '2', '3', '4')
        }

        request = self.factory.post(pth, data=data)
        form = self.TestFormWithManager(request.POST, request.FILES)

        if form.is_valid():
            form.process_files_for('uploads')
            cleaned_data = form.cleaned_data

        self.assertEqual(len(cleaned_data.get('uploads')), 3)


    def tearDown(self):
        remove_files()
