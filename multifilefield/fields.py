import math, floppyforms as forms

from django.core.exceptions import ValidationError

from multifilefield.widgets import ClearableFilesWidget, ClearCheckboxSelectMultipleWidget, FilesInputWidget


class FilesField(forms.FileField):
    """This field is a modified file field that handles
    multiple files rather than a single file."""

    widget = FilesInputWidget


    default_error_messages = {
        'min_num': u'No less than %(min_num)s files uploaded at a time, please (received %(num_files)s).',
        'max_num': u'No more than %(max_num)s files uploaded at a time, please (received %(num_files)s).',
        'file_size': u'File %(uploaded_file_name)s exceeds maximum upload size of %(max_size)s.',
    }


    def __init__(self, *args, **kwargs):
        self.min_num        = kwargs.pop('min_num', 0)
        self.max_num        = kwargs.pop('max_num', None)
        self.max_file_size  = kwargs.pop('max_file_size', None)

        super(FilesField, self).__init__(*args, **kwargs)


    def to_python(self, data):
        ret = []
        for item in data:
            i = super(FilesField, self).to_python(item)
            if i:
                ret.append(i)
        return ret


    def clean(self, data, initial=None):
        return super(FilesField, self).clean(data, initial)


    def humanize(self, nbytes):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

        rank = int((math.log10(nbytes))/3)
        rank = min(rank, len(suffixes) - 1)
        human = nbytes / (1024.0 ** rank)
        f = ('%.2f' % human).rstrip('0').rstrip('.')

        return '%s %s' % (f, suffixes[rank])


    def validate(self, data):
        super(FilesField, self).validate(data)

        uploaded_files = data
        num_files = len(uploaded_files)

        if len(uploaded_files) and not uploaded_files[0]:
            num_files = 0

        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})

        if self.max_file_size:
            for uploaded_file in uploaded_files:
                if uploaded_file.size > self.max_file_size:
                    raise ValidationError(self.error_messages['file_size'] % {
                        'uploaded_file_name': uploaded_file.name,
                        'max_size': self.humanize(self.max_file_size)})



class ClearableFilesField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):

        default_error_messages = {
            'total_num': u'No more than %(total_num)s files in total, please (tried %(attempt_num)s).',
        }

        required        = kwargs.pop('required', False)
        label           = kwargs.pop('label', 'Attach files')
        max_file_size   = kwargs.pop('max_file_size', 1024*1024*5)
        max_num_files   = kwargs.pop('max_num_files', 5)
        min_num_files   = kwargs.pop('min_num_files', 0)

        self.max_num_uploaded   = kwargs.pop('max_num_uploaded', None)
        self.FileCls            = kwargs.pop('model')
        self.queryset           = kwargs.pop('queryset', [])


        upload_field = FilesField(
                label = None,
                max_num = max_num_files,
                min_num = min_num_files,
                max_file_size = max_file_size)


        clear_field = forms.MultipleChoiceField(
                label = None,
                choices = self.get_file_choices(),
                widget = ClearCheckboxSelectMultipleWidget)


        fields = [upload_field, clear_field]
        widgets = [upload_field.widget, clear_field.widget]
        widget = ClearableFilesWidget(widgets = widgets)


        super(ClearableFilesField, self).__init__(
                label = label,
                widget = widget,
                fields = fields)


    def get_file_choices(self):
        return [(file_obj.id, file_obj) for file_obj in self.queryset]


    def validate(self, data_list):
        if self.max_num_uploaded and data_list:
            files_to_upload = data_list[0]
            files_to_delete = data_list[1]

            files_total = len(list(self.queryset))
            files_total -= len(files_to_delete)
            files_total += len(files_to_upload)

            if files_total > self.max_num_uploaded:
                raise ValidationError(self.error_messages['total_num'] % {
                    'total_num': max_num_uploaded,
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

        data = (self.queryset, files_to_upload, files_to_delete)

        self.validate(data)

        return data
