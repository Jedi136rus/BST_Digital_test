from django import forms
from django.core.validators import validate_slug


class RobotForm(forms.Form):
    serial = forms.CharField(max_length=5, required=False)
    model = forms.CharField(max_length=2, required=True, validators=[validate_slug])
    version = forms.CharField(max_length=2, required=True, validators=[validate_slug])
    created = forms.DateTimeField(required=True)
