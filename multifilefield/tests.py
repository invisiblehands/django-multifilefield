from django import forms

from django.core.exceptions import ValidationError
from django.test import TestCase

from multifilefield import ClearableFilesField
from multifilefield.models import UploadedFile



class ClearableFilesFieldTest(TestCase):
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

        clearable_files_field = ClearableFilesField(
            required = False,
            model = UploadedFile,
            queryset = UploadedFile.objects.all()
            label = 'Upload files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0)


    def test_init_queryset_maximum(self):
        """Test that initializing the field doesn't break."""

        clearable_files_field = ClearableFilesField(
            required = False,
            model = UploadedFile,
            queryset = UploadedFile.objects.all()
            label = 'Upload files',
            max_file_size = 1024*1024*5,
            max_num_files = 5,
            min_num_files = 0,
            max_num_uploaded = 10)

        #self.assertEqual()
