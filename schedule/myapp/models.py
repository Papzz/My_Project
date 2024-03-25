import string  # nodrošina noderīgas konstantes
import random  # bibleoteka, lai izvadīt nejauši izveidotas vērtības sistēmā
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password


# tabula Amats
class Amats(models.Model):
    amata_ID = models.AutoField(primary_key=True, unique=True)
    nosaukums = models.CharField(max_length=30)

    def __str__(self):
        return self.nosaukums


# tabula Darbinieki
class Darbinieki(models.Model):
    darb_ID = models.AutoField(primary_key=True, unique=True)
    amata_ID = models.ForeignKey(Amats, on_delete=models.SET_NULL, null=True)
    vards = models.CharField(max_length=15)
    uzvards = models.CharField(max_length=25)
    personas_kods = models.CharField(max_length=12)
    talrunis = models.CharField(max_length=8)
    dz_datums = models.DateField()
    uzsak_datums = models.DateField()
    prasmes = models.CharField(max_length=100, blank=True, null=True)
    login = models.CharField(max_length=20)
    parole = models.CharField(max_length=25)
    menedzeris = models.BooleanField(default=False)

    def __str__(self):
        return self.vards + ' ' + self.uzvards

    def save(self, *args, **kwargs):
        # Перед сохранением хешируем пароль
        self.parole = make_password(self.parole)
        super(Darbinieki, self).save(*args, **kwargs)


# generet nejaušu remonta numuru
def generate_unique_seven_digit_code():
    digits = [str(i) for i in range(1, 10)]
    code = ''.join(random.sample(digits, k=7))
    return code


# geņeret nejaušu paroli
def generate_random_code():
    characters = string.digits + string.ascii_uppercase
    return ''.join(random.choice(characters) for _ in range(4))


# tabula Pakalpojums
class Pakalpojums(models.Model):
    pak_ID = models.AutoField(primary_key=True, unique=True)
    r_numurs = models.CharField(max_length=7, default=generate_unique_seven_digit_code)
    k_parole = models.CharField(max_length=4, default=generate_random_code)
    nosaukums = models.CharField(max_length=50)
    klients = models.CharField(max_length=50)
    k_talrunis = models.CharField(max_length=8)
    k_epasts = models.EmailField(max_length=50)
    datums = models.DateField()
    laiks = models.TimeField()
    vieta = models.CharField(max_length=40)
    sit_aprakts = models.TextField(max_length=300)
    darb_ID = models.ForeignKey(Darbinieki, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(null=True)
    darb_apraksts = models.TextField(max_length=300, default='0')
    darb_kval = models.SmallIntegerField(default='0')
    dar_atrums = models.SmallIntegerField(default='0')
    apkalposanas_lim = models.SmallIntegerField(default='0')
    ats_apraksts = models.TextField(max_length=150, default='0')

    def __str__(self):
        return f"{self.nosaukums} {self.klients} {self.datums.strftime('%Y-%m-%d')} {self.laiks.strftime('%H:%M:%S')}"


# Parbaude vai remonta numurs ir unikals skaitlis
@receiver(pre_save, sender=Pakalpojums)
def set_unique_seven_digit_code(sender, instance, **kwargs):
    if not instance.r_numurs:
        instance.r_numurs = generate_unique_seven_digit_code()
