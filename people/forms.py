from django import forms

from people.models import Waiver


class Html5DateInput(forms.DateInput):
    input_type = 'date'


class WaiverForm(forms.ModelForm):
    phone = forms.RegexField(
        regex=r'\d{10,15}$',
        error_message="Only numbers are allowed. Ex: 8135558888"
    )

    def __init__(self, *args, **kwargs):
        super(WaiverForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.__class__ != forms.BooleanField:
                field.widget.attrs['class'] =  'form-control'
            if field.__class__ == forms.DateField:
                field.widget.attrs['type'] = 'date'
            if name == "dob":
                field.label = "Date of Birth"

    class Meta:
        model = Waiver
        exclude = ('created', 'confirmed', 'hash')
        widgets = {
            'dob': Html5DateInput()
        }
