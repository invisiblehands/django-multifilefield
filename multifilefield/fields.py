import math, floppyforms as forms

from django.core.exceptions import ValidationError

from multifilefield.widgets import ClearableFilesWidget, ClearCheckboxSelectMultipleWidget, FilesInputWidget


class NoFileFieldNameException(Exception):
    pass


class RemoveFilesField(forms.MultipleChoiceField):
    """This field is a modified multiplechoicefield that displays
    a list of uploaded files allowing the user to choose which
    they would like to clear."""

    widget = ClearCheckboxSelectMultipleWidget

    def __init__(self, *args, **kwargs):
        super(RemoveFilesField, self).__init__(*args, **kwargs)



class AddFilesField(forms.FileField):
    """This field is a modified file field that handles
    multiple files rather than a single file."""

    widget = FilesInputWidget


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
            'total_num': u'No more than %(total_num)s files in total, please (tried %(attempt_num)s).',
        }

        required            = kwargs.pop('required', False)
        label               = kwargs.pop('label', 'Uploads')
        add_label           = kwargs.pop('add_label', 'Attach files:')
        add_help_text       = kwargs.pop('add_help_text', 'Hold shift to select multiple files.  To upload selected files click save.')
        remove_label        = kwargs.pop('remove_label', 'Remove attached files:')
        remove_help_text    = kwargs.pop('remove_help_text', 'To remove attached files click their associated checkbox and click save.')

        max_file_size   = kwargs.pop('max_file_size', 1024*1024*5)
        max_num_files   = kwargs.pop('max_num_files', 5)
        min_num_files   = kwargs.pop('min_num_files', 0)

        self.max_num_total  = kwargs.pop('max_num_total', None)
        self.queryset       = kwargs.pop('queryset', None)
        self.filefield_name = kwargs.pop('filefield_name', None)


        if self.queryset and not self.filefield_name:
            raise NoFileFieldNameException


        choices = []
        if self.queryset:
            for uploaded_file in self.queryset:
                choices.append((uploaded_file.id, getattr(uploaded_file, self.filefield_name)))


        add_field = AddFilesField(
            label = add_label,
            help_text = add_help_text,
            max_num = max_num_files,
            min_num = min_num_files,
            max_file_size = max_file_size,
            required = required)


        remove_field = RemoveFilesField(
            label = remove_label,
            help_text = remove_help_text,
            choices = choices,
            required = False)


        fields = [add_field, remove_field]
        widgets = [add_field.widget, remove_field.widget]
        widget = ClearableFilesWidget(widgets = widgets)


        super(MultiFileField, self).__init__(
            label = label,
            widget = widget,
            fields = fields,
            required = required)


    def validate(self, data_list):
        if self.max_num_total and data_list:
            files_to_upload = data_list[0]
            files_to_delete = data_list[1]

            files_total = len(list(self.queryset))
            files_total -= len(files_to_delete)
            files_total += len(files_to_upload)

            if files_total > self.max_num_total:
                raise ValidationError(self.error_messages['total_num'] % {
                    'total_num': max_num_total,
                    'attempt_num': files_total})


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
