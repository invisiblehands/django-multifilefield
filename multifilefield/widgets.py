import six, copy, floppyforms as forms

from itertools import chain


class ClearableFilesWidget(forms.MultiWidget):
    def decompress(self, value):
        return [value, None]

    def render(self, name, value, *args, **kwargs):
        return super(ClearableFilesWidget, self).render(name, value, *args, **kwargs)

    def format_output(self, rendered_widgets):
        return super(ClearableFilesWidget, self).format_output(rendered_widgets)



class ClearCheckboxSelectMultipleWidget(forms.CheckboxSelectMultiple):
    template_name = 'floppyforms/remove-files.html'

    def get_context(self, name, value, attrs=None, choices=()):
        if not hasattr(value, '__iter__') or isinstance(value, six.string_types):
            value = [value]

        context = super(ClearCheckboxSelectMultipleWidget, self).get_context(name, value, attrs)
        context['attrs']['multiple'] = 'multiple'

        new_choices = []
        for option_value, uploaded_file in chain(self.choices, choices):
            option_label = uploaded_file.basename
            url = uploaded_file.get_absolute_url()
            new_choices.append((option_value, option_label, url))

        context['choices'] = new_choices

        return context



class FilesInputWidget(forms.FileInput):
    template_name = 'floppyforms/add-files.html'

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
