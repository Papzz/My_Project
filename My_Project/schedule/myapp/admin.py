from django.contrib import admin
from .models import *
from .models import Darbinieki
from .models import Pakalpojums

# Register your models here.

admin.site.register(PakTip)
admin.site.register(Darbinieki)
admin.site.register(Pakalpojums)
admin.site.register(PakInfo)
