from django import forms
from . import models


class StorismaTermAdminForm(forms.ModelForm):
    class Meta:
        model = models.StorismaTerm
        exclude = ['attribute']