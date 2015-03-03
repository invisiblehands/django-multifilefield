from .fields import MultiFileField



class NoQuerySetException(Exception):
    pass


class NoStorageException(Exception):
    pass


class FormNotValidException(Exception):
    pass



class MultiFileFieldMixin():
    def process_files(self):
        """ Process files for each field that is a multifilefield.
            """

        if not self.is_valid():
            raise FormNotValidException

        for (fieldname, field) in self.fields:
            if isinstance (field, MultiFileField):
                self.process_files_for(fieldname)
        return self.cleaned_data


    def process_files_for(self, fieldname):
        """ Cleaned multifilefield data structure is a tuple (arg1, arg2).
            arg1 (to_add) = [file_obj] (list of uploaded file objects to add),
            arg2 (to_remove) [file_id] (list of file_ids to remove).

            Currently this only works with queryset argument.
            """


        if not self.is_valid():
            raise FormNotValidException


        field = self.fields[fieldname]
        storage = field.storage

        if not storage:
            raise NoStorageException

        field_data = self.cleaned_data.pop(fieldname, None)

        original_set = []
        if field_data and isinstance(field_data, tuple):
            added = field_data[0]
            removed = field_data[1]

            if removed:
                field.delete_files(removed)

            if added:
                 field.upload_files(added)

            self.cleaned_data[fieldname] = processed_data = field.get_processed()

        return processed_data
