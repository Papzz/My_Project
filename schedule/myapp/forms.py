from .models import Amats
from .models import Darbinieki
from .models import Pakalpojums
from django import forms


class MemberForm(forms.ModelForm):
    class Meta:
        model = Darbinieki
        fields = ['vards', 'uzvards', 'personas_kods', 'talrunis', 'dz_datums', 'uzsak_datums', 'prasmes', 'login',
                  'parole']


class ServiceForm(forms.ModelForm):
    darb_ID = forms.ModelChoiceField(queryset=Darbinieki.objects.all(), label='Darbinieks', required=False)

    class Meta:
        model = Pakalpojums
        fields = ['nosaukums', 'klients', 'k_talrunis', 'k_epasts', 'datums', 'laiks', 'vieta', 'sit_aprakts',
                  'darb_ID']

    def __init__(self, *args, **kwargs):
        initial_darb_ID = kwargs.pop('initial_darb_ID', None)
        super(ServiceForm, self).__init__(*args, **kwargs)

        if initial_darb_ID:
            self.initial['darb_ID'] = initial_darb_ID


class MemberForm(forms.ModelForm):
    class Meta:
        model = Darbinieki
        fields = ['vards', 'uzvards', 'personas_kods', 'talrunis', 'dz_datums', 'uzsak_datums', 'prasmes', 'login',
                  'parole']


class AmatsForm(forms.ModelForm):
    class Meta:
        model = Amats
        fields = ['nosaukums']


class MemberEditForm(forms.ModelForm):
    class Meta:
        model = Darbinieki
        fields = ['vards', 'uzvards', 'amata_ID', 'personas_kods', 'talrunis', 'dz_datums', 'uzsak_datums', 'prasmes',
                  'darb_ID']

    amata_ID = forms.ModelChoiceField(queryset=Amats.objects.all(), label='Amats', empty_label=None)

    def clean_personas_kods(self):
        personas_kods = self.cleaned_data.get('personas_kods')
        if personas_kods and len(personas_kods) > 12:
            raise forms.ValidationError("Personas kods should be at most 12 characters long.")
        return personas_kods

    def __init__(self, *args, **kwargs):
        super(MemberEditForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance'].amata_ID:
            self.initial['amata_ID'] = kwargs['instance'].amata_ID


class ServiceEditForm(forms.ModelForm):
    class Meta:
        model = Pakalpojums
        fields = ['nosaukums', 'klients', 'k_talrunis', 'k_epasts', 'datums', 'laiks', 'vieta', 'sit_aprakts',
                  'darb_ID']


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
        model = Pakalpojums
        fields = ['darb_apraksts']


class ChangeStatusForm(forms.Form):
    pak_ID = forms.IntegerField()
