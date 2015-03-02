import six, copy, floppyforms as forms

from itertools import chain


class MultiFileWidget(forms.MultiWidget):
    def decompress(self, value):
        return [value, None]

    def render(self, name, value, *args, **kwargs):
        return super(MultiFileWidget, self).render(name, value, *args, **kwargs)

    def format_output(self, rendered_widgets):
        return super(MultiFileWidget, self).format_output(rendered_widgets)



class AddFilesWidget(forms.FileInput):
    template_name = 'floppyforms/add-files.html'

    def __init__(self, *args, **kwargs):
        super(AddFilesWidget, self).__init__(*args, **kwargs)


    def render(self, name, value, attrs = {}):
        copied_attrs = copy.copy(attrs)
        copied_attrs['multiple'] = 'multiple'

        return super(AddFilesWidget, self).render(name, value, copied_attrs)


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



class ClearFilesWidget(forms.CheckboxSelectMultiple):
    template_name = 'floppyforms/clear-files.html'

    def get_context(self, name, value, attrs=None):
        if not hasattr(value, '__iter__') or isinstance(value, six.string_types):
            value = [value]

        context = super(ClearFilesWidget, self).get_context(name, value, attrs)
        context['attrs']['multiple'] = 'multiple'
        context['choices'] = self.choices

        return context
