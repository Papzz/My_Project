from django.contrib import admin
from . models import Amats
from . models import Darbinieki
from . models import Pakalpojums

# Register your models here.

admin.site.register(Amats)
admin.site.register(Darbinieki)
admin.site.register(Pakalpojums)
