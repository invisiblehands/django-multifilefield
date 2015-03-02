import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class NoQuerySetException(Exception):
    pass


class FormNotValidException(Exception):
    pass


class MultiFileFieldMixin():
    def get_storage(self):
        location = getattr(settings, 'MULTIFILEFIELD_ROOT', settings.MEDIA_ROOT)
        base_url = getattr(settings, 'MULTIFILEFIELD_URL', settings.MEDIA_URL)

        return FileSystemStorage(location = location, base_url = base_url)


    def delete_file(self, queryset, file_id):
        storage = self.get_storage()

        try:
            uploaded_file = queryset.get(id = int(file_id))
            storage.delete(uploaded_file.basename)
            uploaded_file.delete()
        except ValueError, e:
            pass

        return uploaded_file


    def upload_file(self, queryset, file_obj):
        storage = self.get_storage()

        relpath = os.path.normpath(storage.get_valid_name(os.path.basename(file_obj.name)))
        filename = storage.save(relpath, file_obj)
        uploaded_file = queryset.create(upload = filename)

        return uploaded_file


    def delete_files(self, queryset, file_ids):
        files = [self.delete_file(queryset, file_id) for file_id in file_ids]
        return files


    def upload_files(self, queryset, files):
        files = [self.upload_file(queryset, file_obj) for file_obj in files]
        return files


    def process_files_for(self, fieldname):
        """ Cleaned multifilefield data structure is a tuple.
            to_add (list of file to add),
            to_remove (list of ids to remove) """


        if not self.is_valid():
            raise FormNotValidException


        field = self.fields[fieldname]
        queryset = field.queryset


        if not queryset:
            raise NoQuerySetException

        field_data = self.cleaned_data.pop(fieldname, None)

        original_set = []
        if field_data and isinstance(field_data, tuple):
            added = field_data[0]
            removed = field_data[1]

            if removed:
                self.delete_files(queryset, removed)

            if added:
                 self.upload_files(queryset, added)

            processed_data = queryset.all()
            self.cleaned_data[fieldname] = processed_data

        return processed_data



def process_form(form):
    ids = form.process_files('uploads')
    return ids
