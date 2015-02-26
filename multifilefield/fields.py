import math, floppyforms as forms

from django.core.exceptions import ValidationError

from multifilefield.models import UploadedFile
from multifielfield.widgets import ClearableFilesWidget, ClearCheckboxSelectMultipleWidget, FilesInputWidget


class FilesField(forms.FileField):
    widget = FilesInputWidget
    default_error_messages = {
        'min_num': u'No less than %(min_num)s files uploaded at a time, please (received %(num_files)s).',
        'max_num': u'No more than %(max_num)s files uploaded at a time, please (received %(num_files)s).',
        'file_size': u'File %(uploaded_file_name)s exceeds maximum upload size of %(max_size)s.',
    }


    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('maximum_file_size', None)

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

        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})

        if self.maximum_file_size:
            for uploaded_file in data:
                if uploaded_file.size > self.maximum_file_size:
                    raise ValidationError(self.error_messages['file_size'] % {
                        'uploaded_file_name': uploaded_file.name,
                        'max_size': self.humanize(self.maximum_file_size)})



class ClearableFilesField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        kwargs['required'] = False

        label = kwargs.pop('label')
        label = 'Attach files'

        self.uploaded_original = kwargs.pop('uploaded', [])
        self.uploaded_files = []

        for upload in self.uploaded_original:
            self.uploaded_files.extend(UploadedFile.objects.filter(id=upload))


        choices = [(uploaded_file.id, uploaded_file) for uploaded_file in self.uploaded_files]
        self.files = choices
        self.choices = choices

        upload_field = FilesField(
                label = None,
                max_num = 5,
                min_num = 0,
                maximum_file_size = 1024*1024*5,
                *args,
                **kwargs)


        clear_field = forms.MultipleChoiceField(
                label = None,
                choices = choices,
                widget = ClearCheckboxSelectMultipleWidget,
                *args,
                **kwargs)

        fields = [upload_field, clear_field]
        widgets = [upload_field.widget, clear_field.widget]

        super(ClearableFilesField, self).__init__(
                label = label,
                widget = ClearableFilesWidget(widgets = widgets),
                fields = fields,
                *args,
                **kwargs)


    def compress(self, data_list):
        files_to_upload = []
        files_to_delete = []

        if data_list:
            files_to_upload = data_list[0]
            files_to_delete = data_list[1]

        return (self.uploaded_original, files_to_upload, files_to_delete)
