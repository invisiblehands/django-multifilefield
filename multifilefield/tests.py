import mock
from django import forms

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import Storage
from django.test import TestCase

from multifilefield import ClearableFilesField
from multifilefield.models import UploadedFile


# note to self -- maybe don't need to use mock.  let's see.
# http://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django


class ClearableFilesFieldTest(TestCase):
    def setUp(self):
        self.create_mock_files()
        self.create_mock_storage()


    def create_mock_files(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.jpg'

        self.file_mock = file_mock

    def create_mock_storage():
        storage_mock = mock.MagicMock(spec=Storage, name='StorageMock')
        storage_mock.url = mock.MagicMock(name='url')
        storage_mock.url.return_value = '/tmp/test1.jpg'

        self.storage_mock = storage_mock

        # with mock.patch('django.core.files.storage.default_storage._wrapped', storage_mock):
        #     # The asset is saved to the database but our mock storage
        #     # system is used so we don't touch the filesystem
        #     asset.save()

    def test_init(self):
        """Test that initializing the field doesn't break."""

        clearable_files_field = ClearableFilesField(
            required = False,
            model = UploadedFile,
            label ='Upload files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)


    def test_init_queryset(self):
        """Test that initializing the field doesn't break."""

        queryset = UploadedFile.objects.all()
        clearable_files_field = ClearableFilesField(
            required = False,
            model = UploadedFile,
            queryset = queryset,
            label = 'Upload files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)


    def test_init_queryset_maximum(self):
        """Test that initializing the field doesn't break."""

        queryset = UploadedFile.objects.all()
        clearable_files_field = ClearableFilesField(
            required = False,
            model = UploadedFile,
            queryset = queryset,
            label = 'Upload files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0,
            max_num_uploaded = 10)

        #self.assertEqual()
