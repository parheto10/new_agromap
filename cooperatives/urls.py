from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

from .views import (
    coop_dashboard,
    add_section,
    add_sous_section,
    export_parcelles_to_pdf,
    producteurs,
    # cooperative,
    prod_update,
    prod_delete,
    parcelles,
    parcelle_delete,
    # planting,
    # planting_update,
    formation,
    detail_formation,
    AddPlantingView,
    export_planting_xls,
    # use Ajax and jquery request
    my_section,
    export_producteur_csv,
    # PlantingDelete,
    export_prods_to_pdf,
    export_prod_xls,
    export_parcelle_xls,
    export_plant_xls, Editformation, parcelle_update, update_section, delete_section, export_section_xls,
    update_sous_section,
    export_sous_section_xls, export_formation_xls, delete_sous_section, ParcellesMapView, parcelle_list, ReceptionView,
    folium_map, PlantingList, detail_planting, coopdetailPlantings, CoopPlantings, getParcelleCoop, map_by_cooperative,
    # delete_sous_section, export_sous_section_xls, export_formation_xls, my_parcelles, ParcellesView,
    # load_section
)

app_name='cooperatives'

urlpatterns = [
    # Patient
    # path('cooperative/<int:id>', cooperative, name='cooperative'),
    path('producteur/<str:code>/modifier', prod_update, name='modifier'),
    path('producteur/<str:code>/supprimer', prod_delete, name='del_producteur'),
    # path('parcelle/<int:id>', parcelle_delete, name='del_parcelle'),
    path('parcelle/<int:id>/modifier', parcelle_update, name='edit_parcelle'),
    path('parcelle/<int:id>/supprimer', parcelle_delete, name='parcelle_delete'),
    path('section/<int:id>/modifier', update_section, name='update_section'),
    path('section/<int:id>/delete/supprimer', delete_section, name='delete_section'),
    path('sous_section/<int:id>/modifier', update_sous_section, name='update_sous_section'),
    path('sous_section/<int:id>/supprimer', delete_sous_section, name='delete_sous_section'),
    path('dashboard/', coop_dashboard, name='dashboard'),
    path('sections/', add_section, name='section'),
    path('sous_sections/', add_sous_section, name='sous_sections'),
    path('formation/', formation, name='formations'),
    path('Editformation/<int:id>', Editformation, name='Editformation'),
    path('formation/<int:id>', detail_formation, name='formation'),
    path('producteurs/', producteurs, name='producteurs'),
    path('parcelles/', parcelles, name='parcelles'),
    #path('my_parcelles/', my_parcelles, name='my_parcelles'),
    # path('plantings/', planting, name='planting'),
    path('planting_coop/', CoopPlantings, name='CoopPlantings'),
    path('coopdetailPlantings/', coopdetailPlantings, name='coopdetailPlantings'),
    path('plantings/<int:id>/', detail_planting, name='suivi_planting'),
    path('add_planting/', AddPlantingView.as_view(), name='add_planting'),
# detail_planting
    # path('planting/<int:pk>', PlantingDelete.as_view(), name='planting-delete'),
    path('folium_map/', folium_map, name='folium_map'),

    #get Ajax Data
    # path('parcelles/data', ParcellesView.as_view(), name="parcelles_data"),
    path('parcelle_list/', parcelle_list, name="parcelle_list"),
    path('parcelles_list/', ParcellesMapView.as_view(), name="parcelle_list"),

    #path('my-section/', my_section, name='my_section'),
    # path('ajax/load-section/', load_section, name='ajax_load_section'),

    #Exportation de Données En Excel
    # path('export/csv/', export_producteur_csv, name='export_producteur_csv'),
    path('producteurs/xls/', export_prod_xls, name='export_prod_xls'),
    path('sections/xls/', export_section_xls, name='export_section_xls'),
    path('sous_sections/xls/', export_sous_section_xls, name='export_sous_section_xls'),
    path('parcelles/xls/', export_parcelle_xls, name='export_parcelle_xls'),
    path('plants/xls/', export_plant_xls, name='export_plant_xls'),
    path('formations/xls/', export_formation_xls, name='export_formation_xls'),
    path('plantings/xls/', export_planting_xls, name='export_planting_xls'),

    #Export Données EN PDF
    path('producteurs/pdf/', export_prods_to_pdf, name='export_prods_to_pdf'),
    path('parcelles/pdf/', export_parcelles_to_pdf, name='export_parcelles_to_pdf'),


    path('parcelleCoop/<int:pk>/', getParcelleCoop, name="parcelleCoop"),

    #route des parcelles par cooperative
    path('map_by_cooperative', map_by_cooperative, name="map_by_cooperative"),
]