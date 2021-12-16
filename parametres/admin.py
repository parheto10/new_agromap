from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    Activite,
    Region,
    Campagne,
    Espece,
    Cat_Plant,
    Projet_Cat,
    Cooperative
)

class CooperativeResource(resources.ModelResource):
    class Meta:
        model = Cooperative

class CooperativeAdmin(ImportExportModelAdmin):    
    resource_class = CooperativeResource

class EspeceResource(resources.ModelResource):
    class Meta:
        model = Espece

class EspeceAdmin(ImportExportModelAdmin):    
    resource_class = EspeceResource

admin.site.register(Cooperative, CooperativeAdmin)
admin.site.register(Activite)
admin.site.register(Campagne)
admin.site.register(Espece, EspeceAdmin)
admin.site.register(Prime)
admin.site.register(Origine)
admin.site.register(Projet)
admin.site.register(Region)
admin.site.register(Sous_Prefecture)
admin.site.register(Cat_Plant)
admin.site.register(Projet_Cat)

# Register your models here.
