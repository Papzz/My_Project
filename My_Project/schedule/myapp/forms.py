from .models import Amats
from .models import Darbinieki
from .models import Pakalpojums
from .models import *
from django import forms


class MemberForm(forms.ModelForm):
    class Meta:
        model = Darbinieki
        fields = ['vards', 'uzvards', 'talrunis', 'dz_datums', 'uzsak_datums', 'epasts', 'tehnika', 'montesana',
                  'programm', 'vaditajs', 'tehmont']


class ServiceForm(forms.ModelForm):
    darb_ID = forms.ModelChoiceField(queryset=Darbinieki.objects.all(), label='Darbinieks', required=False)
    paktip_ID = forms.ModelChoiceField(queryset=PakTip.objects.all(), label='paktip', required=True)

    class Meta:
        model = Pakalpojums
        fields = ['nosaukums', 'klients', 'k_talrunis', 'k_epasts', 'datums', 'laiks', 'vieta', 'sit_aprakts',
                  'darb_ID', 'paktip_ID', 'serija_nr', 'komplektacija']
        widgets = {
            'komplektacija': forms.Textarea(
                attrs={'rows': 2, 'cols': 50, 'maxlength': 300, 'placeholder': 'Ievadiet saņemtu komplektāciju'}),
        }

        def __init__(self, *args, **kwargs):
            initial_darb_ID = kwargs.pop('initial_darb_ID', None)
            super(ServiceForm, self).__init__(*args, **kwargs)

            if initial_darb_ID:
                self.initial['darb_ID'] = initial_darb_ID

        def clean_komplektacija(self):
            # Make the field not required
            return self.cleaned_data.get('komplektacija', '')

    def __init__(self, *args, **kwargs):
        initial_darb_ID = kwargs.pop('initial_darb_ID', None)
        super(ServiceForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
        if initial_darb_ID:
            self.initial['darb_ID'] = initial_darb_ID


class AmatsForm(forms.ModelForm):
    class Meta:
        model = Amats
        fields = ['nosaukums']


class MemberEditForm(forms.ModelForm):
    class Meta:
        model = Darbinieki
        fields = ['vards', 'uzvards', 'talrunis', 'dz_datums', 'uzsak_datums',
                  'epasts', 'tehnika', 'montesana', 'programm', 'vaditajs', 'tehmont']


class ServiceEditForm(forms.ModelForm):
    class Meta:
        model = Pakalpojums
        fields = ['nosaukums', 'klients', 'k_talrunis', 'k_epasts', 'datums', 'laiks', 'vieta', 'sit_aprakts',
                  'darb_ID', 'paktip_ID', 'serija_nr', 'komplektacija']


class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=20)
    parole = forms.CharField(label='Parole', widget=forms.PasswordInput())


class UserLoginForm(forms.Form):
    r_numurs = forms.CharField(label='Remonta numurs', max_length=7)
    k_parole = forms.CharField(label='Klienta parole', max_length=4)


class AmatsForm(forms.ModelForm):
    class Meta:
        model = Amats
        fields = ['nosaukums']


class SaveInfoForm(forms.ModelForm):
    class Meta:
        model = Pakalpojums
        fields = ['darb_kval', 'dar_atrums', 'apkalposanas_lim', 'ats_apraksts']


class DarbAprakstsForm(forms.ModelForm):
    class Meta:
        model = PakInfo
        fields = ['darb_apraksts']


class IzbraukumsForm(forms.ModelForm):
    class Meta:
        model = Pakalpojums
        fields = ['nobraukums', 'p_laiks', 'darb_apraksts', 'auto']


class ChangeStatusForm(forms.Form):
    pak_ID = forms.IntegerField()
