import copy, math, six, floppyforms as forms

from itertools import chain

from django.utils.encoding import force_unicode
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from multifilefield.models import UploadedFile


class ClearableFilesWidget(forms.MultiWidget):
    def decompress(self, value):
        return [value, None]

    def render(self, name, value, *args, **kwargs):
        return super(ClearableFilesWidget, self).render(name, value, *args, **kwargs)

    def format_output(self, rendered_widgets):
        return super(ClearableFilesWidget, self).format_output(rendered_widgets)



class ClearCheckboxSelectMultipleWidget(forms.CheckboxSelectMultiple):
    template_name = 'floppyforms/clearcheckbox_select.html'

    def get_context(self, name, value, attrs=None, choices=()):
        if not hasattr(value, '__iter__') or isinstance(value,
                                                        six.string_types):
            value = [value]

        context = super(ClearCheckboxSelectMultipleWidget, self).get_context(name, value, attrs)

        if self.allow_multiple_selected:
            context['attrs']['multiple'] = "multiple"

        new_choices = []
        for option_value, uploaded_file in chain(self.choices, choices):
            option_label = uploaded_file.basename
            url = uploaded_file.get_absolute_url()
            new_choices.append((option_value, option_label, url))

        context["choices"] = new_choices

        return context



class FilesInputWidget(forms.FileInput):
    template_name = 'floppyforms/filesinput.html'

    def __init__(self, *args, **kwargs):
        super(FilesInputWidget, self).__init__(*args, **kwargs)


    def render(self, name, value, attrs = {}):
        copied_attrs = copy.copy(attrs)
        copied_attrs['multiple'] = 'multiple'
        return super(FilesInputWidget, self).render(name, value, copied_attrs)


    def value_from_datadict(self, data, files, name):
        values = []
        if files:
            if hasattr(files, 'getlist'):
                values = files.getlist(name)
            else:
                value = files.get(name, None)
                if value:
                    values = [value]

        return values



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
