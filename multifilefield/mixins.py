from django.core.files.storage import FileSystemStorage


class NoManagerException(Exception):
    pass


class MultiFileFieldMixin():
    def get_storage(self):
        location = settings.STATIC_ROOT
        base_url = settings.STATIC_URL

        return FileSystemStorage(location = location, base_url = base_url)


    def delete_file(self, filename):
        storage = self.get_storage()

        try:
            uploaded_file = self.manager.get(id = filename)
            storage.delete(uploaded_file.basename)
            uploaded_file.delete()
        except ValueError, e:
            pass

        return filename


    def upload_file(self, file_obj):
        storage = self.get_storage()

        relpath = os.path.normpath(storage.get_valid_name(os.path.basename(file_obj.name)))
        filename = storage.save(relpath, file_obj)
        uploaded_file = self.manager.create(upload = filename)

        return uploaded_file.id


    def delete_files(self, filenames):
        return [self.delete_file(file_id) for file_id in filenames]


    def upload_files(self, files):
        filenames = [self.upload_file(file_obj) for file_obj in files]
        return filenames


    def process_files(form, fieldname):
        """ cleaned_clearableupload is tuple.
            original_queryset,
            to_add (list of file to add),
            to_remove (list of ids to remove) """

        self.manager = form.fields[fieldname].manager

        if not self.manager:
            raise NoManagerException

        form_data = form.cleaned_data
        field_data = form_data.pop(fieldname, None)
        original_set = []
        if field_data:
            original = field_data[0]
            added = field_data[1]
            removed = field_data[2]

            original_set = set(original)

            if removed:
                removed_set = set(self.delete_files(removed))
                original_set.difference_update(removed_set)

            if added:
                added_set = set(self.upload_files(added))
                original_set.update(added_set)

        return list(original_set)




def process_form(form):
    # multifilefield is called 'uploads'
    # make sure the mixin has been subclassed by the form.
    # uploads the files and returns a list of ids.
    ids = form.process_files('uploads')

    return ids
