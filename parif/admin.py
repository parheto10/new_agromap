from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (
    Projet, Section, Parcelle,
    Planting, DetailPlanting, Monitoring
)

class ProjetAdmin(ImportExportModelAdmin):
    list_display = ['id', 'code', 'libelle', 'chef']
admin.site.register(Projet, ProjetAdmin)

class SectionAdmin(ImportExportModelAdmin):
    list_display = ['id', 'cooperative', 'libelle', 'responsable', 'contacts']
admin.site.register(Section, SectionAdmin)

class ParcelleAdmin(ImportExportModelAdmin):
    list_display = ['id', 'cooperative', 'projet', 'code_parcelle', 'localite', 'proprietaire', 'latitude', 'longitude', 'superficie', 'culture', 'culture_associee', 'type']
    search_fields = ['code_parcelle', 'proprietaire', 'localite', 'cooperative', ]
    list_display_links = ['code_parcelle', ]
    list_filter = ['type', 'projet__libelle', ]
admin.site.register(Parcelle, ParcelleAdmin)

class DetailPlantingAdmin(admin.TabularInline):
   model = DetailPlanting
   extra = 0

class PlantingAdmin(ImportExportModelAdmin):
   fields = ('parcelle', 'projet', "campagne", "nb_plant_exitant", "plant_recus", "plant_total", "date")
   list_display = ('parcelle','projet', "campagne", "nb_plant_exitant", "plant_recus", "plant_total", "date")
   list_display_links = ('parcelle',)
   readonly_fields = ["plant_total"]
   inlines = [DetailPlantingAdmin]
admin.site.register(Planting, PlantingAdmin)

# class MinitoringAdmin(admin.TabularInline):
class MinitoringAdmin(ImportExportModelAdmin):
   model = Monitoring
   fields = ['espece', 'mort', 'remplace', 'date', 'mature', 'observation']
   list_display = ['espece', 'mort', 'remplace', 'date', 'mature', 'observation']
admin.site.register(Monitoring, MinitoringAdmin)
# Register your models here.
