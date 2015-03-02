import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class NoManagerException(Exception):
    pass


class FormNotValidException(Exception):
    pass


class MultiFileFieldMixin():
    def get_storage(self):
        location = getattr(settings, 'MULTIFILEFIELD_ROOT', settings.MEDIA_ROOT)
        base_url = getattr(settings, 'MULTIFILEFIELD_URL', settings.MEDIA_URL)

        return FileSystemStorage(location = location, base_url = base_url)


    def delete_file(self, manager, file_id):
        storage = self.get_storage()

        try:
            uploaded_file = manager.get(id = int(file_id))
            storage.delete(uploaded_file.basename)
            uploaded_file.delete()
        except ValueError, e:
            pass

        return uploaded_file


    def upload_file(self, manager, file_obj):
        storage = self.get_storage()

        relpath = os.path.normpath(storage.get_valid_name(os.path.basename(file_obj.name)))
        filename = storage.save(relpath, file_obj)
        uploaded_file = manager.create(upload = filename)

        return uploaded_file


    def delete_files(self, manager, file_ids):
        files = [self.delete_file(manager, file_id) for file_id in file_ids]
        return files


    def upload_files(self, manager, files):
        files = [self.upload_file(manager, file_obj) for file_obj in files]
        return files


    def process_files_for(self, fieldname):
        """ cleaned_clearableupload is tuple.
            original_queryset,
            to_add (list of file to add),
            to_remove (list of ids to remove) """


        if not self.is_valid():
            raise FormNotValidException


        field = self.fields[fieldname]
        manager = self.fields[fieldname].manager


        if not manager:
            raise NoManagerException

        field_data = self.cleaned_data.pop(fieldname, None)

        original_set = []
        if field_data and isinstance(field_data, tuple):
            added = field_data[1]
            removed = field_data[2]

            if removed:
                self.delete_files(manager, removed)

            if added:
                 self.upload_files(manager, added)

            processed_data = manager.all()
            self.cleaned_data[fieldname] = processed_data

        return processed_data



def process_form(form):
    ids = form.process_files('uploads')
    return ids
