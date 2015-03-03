import os, math, floppyforms as forms

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage

from .widgets import MultiFileWidget, AddFilesWidget, ClearFilesWidget


ASSERT_FILE_CHOICES = '"files" argument must be a list of django File objects.'


class NoFileFieldNameException(Exception):
    message = 'QuerySet configuration requires filefield_name'



class ClearFilesField(forms.MultipleChoiceField):
    """This field is a modified multiplechoicefield that displays
    a list of uploaded files allowing the user to choose which
    they would like to clear."""

    widget = ClearFilesWidget

    def __init__(self, *args, **kwargs):
        super(ClearFilesField, self).__init__(*args, **kwargs)



class AddFilesField(forms.FileField):
    """This field is a modified file field that handles
    multiple files rather than a single file."""

    widget = AddFilesWidget


    default_error_messages = {
        'min_num': 'No less than %(min_num)s files uploaded at a time, please (received %(num_files)s).',
        'max_num': 'No more than %(max_num)s files uploaded at a time, please (received %(num_files)s).',
        'file_size': 'File %(uploaded_file_name)s exceeds maximum upload size of %(max_size)s.',
    }


    def __init__(self, *args, **kwargs):
        self.min_num        = kwargs.pop('min_num', 0)
        self.max_num        = kwargs.pop('max_num', None)
        self.max_file_size  = kwargs.pop('max_file_size', None)

        super(AddFilesField, self).__init__(*args, **kwargs)


    def to_python(self, data):
        ret = []
        for item in data:
            i = super(AddFilesField, self).to_python(item)
            if i:
                ret.append(i)
        return ret


    def clean(self, data, initial=None):
        return super(AddFilesField, self).clean(data, initial)


    def humanize(self, nbytes):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

        rank = int((math.log10(nbytes))/3)
        rank = min(rank, len(suffixes) - 1)
        human = nbytes / (1024.0 ** rank)
        f = ('%.2f' % human).rstrip('0').rstrip('.')

        return '%s %s' % (f, suffixes[rank])


    def validate(self, data):
        super(AddFilesField, self).validate(data)

        uploaded_files = data
        num_files = len(uploaded_files)

        if len(uploaded_files) and not uploaded_files[0]:
            num_files = 0

        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {
                'min_num': self.min_num,
                'num_files': num_files})

        if self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {
                'max_num': self.max_num,
                'num_files': num_files})

        if self.max_file_size:
            for uploaded_file in uploaded_files:
                if uploaded_file.size > self.max_file_size:
                    raise ValidationError(self.error_messages['file_size'] % {
                        'uploaded_file_name': uploaded_file.name,
                        'max_size': self.humanize(self.max_file_size)})



class MultiFileField(forms.MultiValueField):
    """
    This is a clearable files field.  It uses the html5 "multiple" attribute
    on a fileupload input to allow for multiple file uploads, if available
    through the browser.  The files are then validated.

    If the developer provides a queryset, this project also provides
    mechanisms for storing files and also populating clearable choices, so
    the user can both upload and clear.
    """

    def __init__(self, *args, **kwargs):
        default_error_messages = {
            'total_num': 'No more than %(total_num)s files in total, please (tried %(attempt_num)s).',
            'required': 'At least one file must be uploaded.'
        }

        label               = kwargs.pop('label', 'Uploads')
        add_label           = kwargs.pop('add_label', 'Attach files:')
        add_help_text       = kwargs.pop('add_help_text', 'Hold shift to select multiple files.  To upload selected files submit form.')
        clear_label         = kwargs.pop('clear_label', 'Clear attached files:')
        clear_help_text     = kwargs.pop('clear_help_text', 'To clear attached files click their associated checkbox and submit form.')

        max_file_size   = kwargs.pop('max_file_size', 1024*1024*5)
        max_num_files   = kwargs.pop('max_num_files', 5)
        min_num_files   = kwargs.pop('min_num_files', 0)

        self._required      = kwargs.pop('required', False)
        self.max_num_total  = kwargs.pop('max_num_total', None)
        self.files          = kwargs.pop('files', None)
        self.queryset       = kwargs.pop('queryset', None)
        self.filefield_name = kwargs.pop('filefield_name', None)
        self.storage        = kwargs.pop('storage', default_storage)

        if self.queryset and not self.filefield_name:
            raise NoFileFieldNameException


        self.choices = choices = self.make_choices_from_arguments()


        add_files = AddFilesField(
            label = add_label,
            help_text = add_help_text,
            max_num = max_num_files,
            min_num = min_num_files,
            max_file_size = max_file_size,
            required = False)


        clear_files = ClearFilesField(
            label = clear_label,
            help_text = clear_help_text,
            choices = choices,
            required = False)


        fields = [add_files, clear_files]
        widgets = [add_files.widget, clear_files.widget]
        widget = MultiFileWidget(widgets = widgets)


        super(MultiFileField, self).__init__(
            label = label,
            widget = widget,
            fields = fields,
            required = False)


    def make_choices_from_arguments(self):
        choices = []
        if self.queryset:
            for file_obj in self.queryset:
                choices.append((file_obj.id, getattr(file_obj, self.filefield_name)))
        elif self.files:
            assert all([isinstance(file_obj, File) for file_obj in self.files]), ASSERT_FILE_CHOICES
            choices = [(file_obj.name.split('/')[-1], file_obj) for file_obj in self.files]
        else:
            # raise NoFilesOrQuerySetException
            pass

        return choices


    def clean(self, *args, **kwargs):
        return super (MultiFileField, self).clean(*args, **kwargs)


    def compress(self, data_list):
        """ This field returns a tuple that expresses the original list
        of uploaded file objects, a second list of new files objects to upload
        and a third list of file objects to delete."""

        files_to_upload = []
        files_to_delete = []

        if data_list:
            files_to_upload = data_list[0]
            files_to_delete = data_list[1]

        data = (files_to_upload, files_to_delete)

        self.validate(data)

        return data


    def validate(self, data_list):
        files_total = len(self.choices)

        if data_list:
            files_to_upload = data_list[0]
            files_to_delete = data_list[1]
            files_total += len(files_to_upload) if files_to_upload else 0
            files_total -= len(files_to_delete) if files_to_delete else 0

        if self._required:
            if files_total == 0:
                raise ValidationError(self.error_messages['required'])

        if self.max_num_total:
            if files_total > self.max_num_total:
                raise ValidationError(self.error_messages['total_num'] % {
                    'total_num': max_num_total,
                    'attempt_num': files_total})


    def get_files(self):
        files = []
        for filename in os.listdir(self.storage.location):
            pth = os.path.join(self.storage.location, filename)
            with open(pth) as f:
                files.append(File(f))

        return files


    def get_processed(self):
        if self.queryset:
            return self.queryset.all()
        elif self.files:
            return self.get_files()


    def delete_file_fs(self, file_name):
        try:
            self.storage.delete(file_name)
        except ValueError, e:
            pass

        return file_name


    def upload_file_fs(self, file_obj):
        relpath = os.path.normpath(self.storage.get_valid_name(os.path.basename(file_obj.name)))
        filename = self.storage.save(relpath, file_obj)

        return file_obj


    def delete_file_queryset(self, file_id):
        try:
            uploaded_file = self.queryset.get(id = int(file_id))
            self.storage.delete(uploaded_file.basename)
            uploaded_file.delete()
        except ValueError, e:
            pass

        return uploaded_file


    def upload_file_queryset(self, file_obj):
        relpath = os.path.normpath(self.storage.get_valid_name(os.path.basename(file_obj.name)))
        filename = self.storage.save(relpath, file_obj)
        uploaded_file = self.queryset.create(upload = filename)

        return uploaded_file


    def delete_files(self, file_ids):
        if self.queryset:
            mth = self.delete_file_queryset
        elif self.files:
            mth = self.delete_file_fs
        else:
            raise NotImplementedError

        files = [mth(file_id) for file_id in file_ids]
        return files


    def upload_files(self, files):
        if self.queryset:
            mth = self.upload_file_queryset
        elif self.files:
            mth = self.upload_file_fs
        else:
            raise NotImplementedError

        files = [mth(file_obj) for file_obj in files]
        return files


