import datetime

import datetime
import os

import requests
from django.conf import settings
from django.contrib.staticfiles import finders
from rest_framework.response import Response
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
# from django.contrib.gis.serializers import geojson
from django.core.serializers import serialize
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import folium
from django_pandas.io import read_frame
from folium import raster_layers, plugins, Popup
import json
from django.template.loader import get_template
from django.views.generic import TemplateView
from folium.plugins import MarkerCluster
from rest_framework.decorators import api_view
from xhtml2pdf import pisa
from django.views import View
from xlrd.formatting import Format

# Import django Serializer Features #
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from parametres.forms import UserForm
from parametres.models import Projet, Espece, Campagne
from parametres.serializers import ParcelleSerializer
from .forms import CoopForm, ProdForm, EditProdForm, ParcelleForm, SectionForm, Sous_SectionForm, \
     FormationForm, DetailFormation, EditFormationForm, EditParcelleForm, Edit_Sous_SectionForm, MonitoringForm, \
    PlantingForm, DetailPlantingForm
from .models import Cooperative, Section, Sous_Section, Producteur, Parcelle, Planting, Formation, Detail_Formation, \
     DetailPlanting, Monitoring
from .serializers import CooperativeSerliazer, ParcelleSerliazer


def is_cooperative(user):
    return user.groups.filter(name='COOPERATIVES').exists()

#@login_required(login_url='connexion')
#@user_passes_test(is_cooperative)
# def cooperative(request, id=None):
#     coop = get_object_or_404(Cooperative, pk=id)
#     producteurs = Producteur.objects.all().filter(section__cooperative_id= coop)
#     nb_producteurs = Producteur.objects.all().filter(section__cooperative_id= coop).count()
#     parcelles = Parcelle.objects.all().filter(propietaire__section__cooperative_id=coop)
#     nb_parcelles = Parcelle.objects.all().filter(propietaire__section__cooperative_id=coop).count()
#     context = {
#         "coop": coop,
#         'cooperative': cooperative,
#         'producteurs': producteurs,
#         'nb_producteurs': nb_producteurs,
#         'parcelles': parcelles,
#         'nb_parcelles': nb_parcelles,
#     }
#     return render(request, "cooperatives/dashboard.html", context)


def coop_dashboard(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    producteurs = Producteur.objects.filter(cooperative_id=cooperative)
    nb_producteurs = Producteur.objects.filter(cooperative_id=cooperative, is_active=True).count()
    nb_formations = Formation.objects.all().filter(cooperative_id=cooperative).count()
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    nb_parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).count()
    Superficie = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    Plants = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('plant_total'))['total']
    section = Section.objects.all().filter(cooperative_id=cooperative)
    section_prod = Section.objects.annotate(nb_producteur=Count('producteurs'))
    section_parcelles = Parcelle.objects.filter(producteur__section_id__in=section).count()
    section_superf = Parcelle.objects.filter(producteur__section_id__in=section).aggregate(total=Sum('superficie'))['total']
    section_planting = DetailPlanting.objects.filter(planting__parcelle__producteur__section_id__in=section).aggregate(total=Sum('nb_plante'))['total']
    # detail_planting = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative)#.annotate(nb_plante=Sum('nb_plante'))
    espece_planting = Espece.objects.all()
    plantings = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plante'))['total']
    coop_plants = DetailPlanting.objects.filter(espece_id__in=espece_planting).aggregate(total=Sum('nb_plante'))['total']
    # plantings = DetailPlanting.objects.values("espece__libelle").filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plante'))['total']
    # print(plantings)
    # espece_planting = DetailPlanting.objects.filter(espece__libelle__in=details_planting).aggregate(total=Sum('nb_plante'))['total']
    # espece_planting = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).annotate(nb_plante=Sum('nb_plante'))
    # print(section_prod)
    # nb_producteurs = sections.producteur.set_all()
    # querysets = Detail_Retrait_plant.objects.values("espece__libelle").filter(retait__pepiniere__cooperative_id=cooperative).annotate(plant_retire=Sum('plant_retire'))
    # semences = Semence_Pepiniere.objects.values("espece_recu__libelle").filter(pepiniere__cooperative_id=cooperative).annotate(qte_recu=Sum('qte_recu'))

    context={
    'cooperative':cooperative,
    'producteurs': producteurs,
    'nb_producteurs': nb_producteurs,
    'nb_formations': nb_formations,
    'section_prod': section_prod,
    'section_parcelles': section_parcelles,
    'section_superf': section_superf,
    'parcelles': parcelles,
    'nb_parcelles': nb_parcelles,
    'Superficie' : Superficie,
    'Plants': Plants,
    'section': section,
    'section_planting': section_planting,
    'espece_planting': espece_planting,
    'plantings': plantings,
    'coop_plants': coop_plants,
    # 'labels': labels,
    # 'data': data,
    # 'mylabels': mylabels,
    # 'mydata': mydata,
    }
    return render(request,'cooperatives/dashboard.html',context=context)

def coopdetailPlantings(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    querysets = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data= {
        'labels':labels,
        'data':data,
    })

# def prod_section(request):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     semences = Semence_Pepiniere.objects.values("espece_recu__libelle").filter(pepiniere__cooperative_id=cooperative).annotate(qte_recu=Sum('qte_recu'))
#     labels = []
#     data = []
#     for stat in semences:
#         labels.append(stat['espece_recu__libelle'])
#         data.append(stat['qte_recu'])
#
#     return JsonResponse(data= {
#         'labels':labels,
#         'data':data,
#     })

def add_section(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.cooperative_id = cooperative.id
            section = section.save()
            # print()
        messages.success(request, "Section Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:section'))
    context = {
        "cooperative": cooperative,
        "sections": sections,
        'form': form,
    }
    return render(request, "cooperatives/sections.html", context)

def update_section(request, id=None):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    instance = get_object_or_404(Section, id=id)
    form = SectionForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.cooperative_id = cooperative.id
        instance.save()
        messages.success(request, "Section Modifié Avec Succès", extra_tags='html_safe')
        return HttpResponseRedirect(reverse('cooperatives:section'))
    context = {
        'instance' : instance,
        'form' : form,
    }
    return render(request, "cooperatives/section_edit.html", context)

def delete_section(request, id=None):
    item = get_object_or_404(Section, id=id)
    if request.method == "POST":
        item.delete()
        messages.error(request, "Section Supprimée Avec Succès")
        return redirect('cooperatives:section')
    context = {
        # 'pepiniere': pepiniere,
        'item': item,
    }
    return render(request, 'cooperatives/section_delete.html', context)
    # item.delete()
    # messages.success(request, "Section Supprimer avec Succès")
    # return HttpResponseRedirect(reverse('cooperatives:section'))

def add_sous_section(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    form = Sous_SectionForm()
    if request.method == 'POST':
        form = Sous_SectionForm(request.POST)
        if form.is_valid():
            sous_section = form.save(commit=False)
            for section in sections:
                sous_section.section_id = section.id
            sous_section = sous_section.save()
            # print()
        messages.success(request, "Sous Section Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:sous_sections'))
    context = {
        "cooperative": cooperative,
        "sous_sections": sous_sections,
        "sections": sections,
        'form': form,
    }
    return render(request, "cooperatives/sous_sections.html", context)

def update_sous_section(request, id=None):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    instance = get_object_or_404(Sous_Section, id=id)
    form = Edit_Sous_SectionForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        # instance.cooperative_id = cooperative.id
        instance.save()
        messages.success(request, "Sous Section Modifié Avec Succès", extra_tags='html_safe')
        return HttpResponseRedirect(reverse('cooperatives:sous_sections'))
    context = {
        'instance' : instance,
        'form' : form,
    }
    return render(request, "cooperatives/sous_section_edit.html", context)

def delete_sous_section(request, id=None):
    item = get_object_or_404(Sous_Section, id=id)
    if request.method == "POST":
        item.delete()
        messages.error(request, "Sous Section Supprimée Avec Succès")
        return redirect('cooperatives:sous_sections')
    context = {
        # 'pepiniere': pepiniere,
        'item': item,
    }
    return render(request, 'cooperatives/sous_section_delete.html', context)

def my_section(request):
    cooperative = request.GET.get("user_id")#Cooperative.objects.get(user_id=request.user.id)
    coop_sections = Section.objects.filter(cooperative_id=cooperative)
    context = {'coop_sections': coop_sections}
    return render(request, 'cooperatives/section.html', context)

def producteurs(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    producteurs = Producteur.objects.filter(cooperative_id=cooperative)#.order_by("-add_le")
    sections = Section.objects.filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)

    prodForm = ProdForm()
    if request.method == 'POST':
        prodForm = ProdForm(request.POST, request.FILES)
        if prodForm.is_valid():
            producteur = prodForm.save(commit=False)
            producteur.cooperative_id = cooperative.id
            for section in sections:
                producteur.section_id = section.id
            for sous_section in sous_sections:
                producteur.sous_section_id = sous_section.id
            producteur = producteur.save()
            # print(producteur)
        messages.success(request, "Producteur Ajouté avec succès")
        return HttpResponseRedirect(reverse('cooperatives:producteurs'))

    context = {
        "cooperative":cooperative,
        "producteurs": producteurs,
        'prodForm': prodForm,
        'sections':sections,
        'sous_sections':sous_sections,

    }
    return render(request, "cooperatives/producteurs.html", context)

def prod_update(request, code=None):
	instance = get_object_or_404(Producteur, code=code)
	form = EditProdForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Producteur Modifié Avec Succès", extra_tags='html_safe')
		return HttpResponseRedirect(reverse('cooperatives:producteurs'))

	context = {
		"instance": instance,
		"form":form,
	}
	return render(request, "cooperatives/prod_edt.html", context)

def prod_delete(request, code=None):
    item = get_object_or_404(Producteur, code=code)
    if request.method == "POST":
        item.delete()
        messages.error(request, "Producteur Supprimer Avec Succès")
        return redirect('cooperatives:producteurs')
    context = {
        'item': item,
    }
    return render(request, 'cooperatives/prod_delete.html', context)

def parcelles(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    prods = Producteur.objects.filter(cooperative_id=cooperative)
    s_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    parcelleForm = ParcelleForm(request.POST or None)
    if request.method == 'POST':
        parcelleForm = ParcelleForm(request.POST, request.FILES)
        if parcelleForm.is_valid():
            parcelle = parcelleForm.save(commit=False)
            # parcelle.producteur_id = prods
            for prod in prods:
                parcelle.producteur_id = prod.id
                if not parcelle.code:
                    tot = Parcelle.objects.filter(producteur_id=prod).count()
                    parcelle.code = "%s-%s" % (parcelle.producteur.code, tot)

            for sect in s_sections:
                parcelle.sous_section_id = sect.id

            parcelle = parcelle.save()
            # print(parcelle)
        messages.success(request, "Parcelle Ajoutés avec succès")
        return HttpResponseRedirect(reverse('cooperatives:parcelles'))

    context = {
        "cooperative":cooperative,
        "parcelles": parcelles,
        'parcelleForm': parcelleForm,
        'producteurs': prods,
        's_sections': s_sections,
    }
    return render(request, "cooperatives/parcelles.html", context)

def parcelle_update(request, id=None):
    instance = get_object_or_404(Parcelle, id=id)
    form = EditParcelleForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Parcelle Modifiée Avec Succès", extra_tags='html_safe')
        return HttpResponseRedirect(reverse('cooperatives:parcelles'))
    context = {
        'instance':instance,
        'form':form
    }
    return render(request, "cooperatives/parcelle_edit.html", context)

def parcelle_delete(request, id=None):
    parcelle = get_object_or_404(Parcelle, id=id)
    if request.method == "POST":
        parcelle.delete()
        messages.error(request, "Parcelle Supprimée Avec Succès")
        return redirect('cooperatives:parcelles')
    context = {
        'parcelle': parcelle,
    }
    return render(request, 'cooperatives/parcelle_delete.html', context)
    # parcelle.delete()
    # messages.success(request, "Parcelle Supprimer avec Succès")
    # return HttpResponseRedirect(reverse('cooperatives:parcelles'))

def detail_parcelles(request, id=None):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    plantings = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
    instance = get_object_or_404(Planting, id=id)
    # details = Details_planting.objects.all().filter(planting_id=instance)

    context = {

    }

    return render(request, 'cooperatives/detail_parcelle', context)


# def planting(request):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     # producteurs = Producteur.objects.all().filter(cooperative=cooperative)
#     parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
#     plantings = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
#     plantingForm = PlantingForm()
#     if request.method == 'POST':
#         plantingForm = PlantingForm(request.POST, request.FILES)
#         if plantingForm.is_valid():
#             planting = plantingForm.save(commit=False)
#             for parcelle in parcelles.iterator():
#                 planting.parcelle_id = parcelle.id
#             planting = planting.save()
#             print(planting)
#             # print(planting.parcelle.producteur)
#         messages.success(request, "Parcelle Ajoutés avec succès")
#         return HttpResponseRedirect(reverse('cooperatives:planting'))
#     context = {
#         "cooperative":cooperative,
#         "parcelles": parcelles,
#         "plantings": plantings,
#         'plantingForm': plantingForm,
#     }
#     return render(request, "cooperatives/plantings.html", context)

# def suivi_planting(request, id=None):
#     instance = get_object_or_404(Planting, id=id)
#     # details = Details_planting.objects.all().filter(planting_id=instance)
#
#     # suiviForm = SuiviPlantingForm()
#     # if request.method == 'POST':
#     #     suiviForm = SuiviPlantingForm(request.POST, request.FILES)
#     #     if suiviForm.is_valid():
#     #         suivi = suiviForm.save(commit=False)
#     #         suivi.planting_id = instance.id
#     #         suivi = suivi.save()
#     #         print(suivi)
#     #     messages.success(request, "Planting Ajouté avec succès")
#     #     return HttpResponseRedirect(reverse('cooperatives:planting'))
#     # context = {
#     #     'instance':instance,
#     #     'details':details,
#     #     'suiviForm':suiviForm,
#     # }
#     # return render(request, 'cooperatives/suivi_planting.html', context)

# def planting_update(request, id=None):
# 	instance = get_object_or_404(Planting, id=id)
# 	# form = PlantingForm(request.POST or None, request.FILES or None, instance=instance)
# 	if form.is_valid():
# 		instance = form.save(commit=False)
# 		instance.save()
# 		messages.success(request, "Modification effectuée avec succès")
# 		return HttpResponseRedirect(reverse('cooperatives:planting'))
#
# 	context = {
# 		"instance": instance,
# 		"form":form,
# 	}
# 	return render(request, "cooperatives/planting_edit.html", context)

#-------------------------------------------------------------------------
## Export to Excel
#-------------------------------------------------------------------------

import csv

from django.http import HttpResponse
from django.contrib.auth.models import User

def export_producteur_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="producteurs.csv"'

    writer = csv.writer(response)
    writer.writerow(['CODE', 'TYPE', 'SECTION', 'GENRE', 'NOM', 'PRENOMS', 'CONTACTS'])
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    # producteurs = Producteur.objects.all().filter(cooperative=cooperative)

    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'code',
        'type_producteur',
        'section__libelle',
        'genre',
        'nom',
        'prenoms',
        'contacts',
    )
    for p in producteurs:
        writer.writerow(p)

    return response

import xlwt

from django.http import HttpResponse
from django.contrib.auth.models import User

def export_prod_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'NOM ET PRENOMS', 'SECTION', 'LOCALITE', 'TYPE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'code',
        'nom',
        'section__libelle',
        'localite',
        'type_producteur',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def export_planting_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'PRODUCTEUR', 'SECTION', 'ESPECE', 'QTE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = DetailPlanting.objects.all().filter(planting__parcelle__producteur__cooperative_id=cooperative.id).values_list(
        'planting__parcelle__code',
        'planting__parcelle__producteur__nom',
        'planting__parcelle__producteur__section__libelle',
        'espece__libelle',
        'nb_plante',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_section_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sections.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sections')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['LIBELLE', 'RESPONSABLE', 'CONTACTS']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Section.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'libelle',
        'responsable',
        'contacts',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_sous_section_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sous Sections.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sous Sections')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['SECTION', 'LIBELLE', 'RESPONSABLE', 'CONTACTS']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Sous_Section.objects.all().filter(section__cooperative_id=cooperative.id).values_list(
        'section__libelle',
        'libelle',
        'responsable',
        'contacts',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_parcelle_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Parcelles.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Parcelles')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'PRODUCETUR', 'SECTION', 'SUPER', 'LONG', 'LAT', 'CULTURE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative.id).values_list(
        'code',
        'producteur__nom',
        'producteur__section__libelle',
        'superficie',
        'longitude',
        'latitude',
        'culture',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_formation_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Formations.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Formations')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['PROJET', 'FORMATEUR', 'INTITULE', 'DEBUT', 'FIN']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    # format2 = xlwt.Workbook({'num_format': 'dd/mm/yy'})
    rows = Formation.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'projet__titre',
        'formateur',
        'libelle',
        'debut',
        'fin',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if isinstance(row[col_num], datetime.datetime):
                DEBUT = row[col_num].strftime('%d/%m/%Y')
                FIN = row[col_num].strftime('%d/%m/%Y')
                ws.write(row_num, col_num, DEBUT, FIN, font_style)
            else:
                ws.write(row_num, col_num, row[col_num], font_style)
            # ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_plant_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Planting.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Plants')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['P.CODE', 'P.NOM', 'P.PRENOMS', 'PARCELLE', 'ESPECE', 'NOMBRE', 'DATE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    rows = Planting.objects.all().filter(parcelle__propietaire__cooperative_id=cooperative.id).values_list(
        'parcelle__propietaire__code',
        'parcelle__propietaire__nom',
        'parcelle__propietaire__prenoms',
        'parcelle__code',
        'espece',
        'nb_plant',
        'date',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_prod_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Producteurs.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Start writing the PDF here
    p.drawString(100, 100, 'Hello world.')
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse

def localisation(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    # section = Section.objects.all().filter(cooperative_id=cooperative)
    sections = Section.objects.all().filter(cooperative_id=cooperative) #Parcelle.objects.filter(producteur__section_id__in=section)
    context = {
        'cooperative': cooperative,
        'parcelles' : parcelles,
        'sections' : sections
    }
    return render(request, 'cooperatives/carte_update.html', context)


def formation(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    formations = Formation.objects.all().filter(cooperative_id=cooperative)
    formationForm = FormationForm()
    if request.method == 'POST':
        formationForm = FormationForm(request.POST, request.FILES)
        if formationForm.is_valid():
            formation = formationForm.save(commit=False)
            formation.cooperative_id = cooperative.id
            formation = formation.save()
            # print(formation)
            # print(planting.parcelle.producteur)
        messages.success(request, "Formation Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:formations'))

    context = {
        'cooperative': cooperative,
        'formations': formations,
        'formationForm': formationForm,
    }
    return render(request, 'cooperatives/formations.html', context)

def Editformation(request, id=None):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    instance = get_object_or_404(Formation, id=id)
    form = EditFormationForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.cooperative_id = cooperative.id
        instance.save()
        instance.save()
        messages.success(request, "Modification Effectuée Avec Succès", extra_tags='html_safe')
        return HttpResponseRedirect(reverse('cooperatives:formations'))

    context = {
        "cooperative":cooperative,
        "instance": instance,
        "form": form,
    }
    return render(request, "cooperatives/edit_formation.html", context)

# def detail_formation(request, id=None):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     # instance = Detail_Formation.objects.get(formation_id=id)
#     instance = get_object_or_404(Formation, id=id)
#     details = Detail_Formation.objects.all().filter(formation_id=instance)
#     participants = Producteur.objects.all().filter(cooperative_id=cooperative)
#     form = DetailFormation()
#     if request.method == 'POST':
#         form = DetailFormation(request.POST, request.FILES)
#         if form.is_valid():
#             detail = form.save(commit=False)
#             detail.formation_id = instance.id
#             # for p in participants:
#                 # detail.
#             detail = detail.save()
#             # print(detail)
#             # print(planting.parcelle.producteur)
#         messages.success(request, "Formation Ajoutée avec succès")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#         # return HttpResponseRedirect(reverse('cooperatives:formations'))
#     # participants = Producteur.objects.all().filter(formation_id=formation)
#     context = {
#         'instance': instance,
#         'details': details,
#         'form': form,
#         'participants': participants,
#     }
#     return render(request, 'cooperatives/detail_formation.html', context)

def detail_formation(request, id=None):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    # instance = Detail_Formation.objects.get(formation_id=id)
    instance = get_object_or_404(Formation, id=id)
    details = Detail_Formation.objects.filter(formation_id=instance)
    participants = Producteur.objects.filter(cooperative_id=cooperative)
    form = DetailFormation()
    if request.method == 'POST':
        form = DetailFormation(request.POST, request.FILES)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.formation_id = instance.id
            detail.save()
            messages.success(request, "Participants Ajoutés avec succès")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = {
        'instance': instance,
        'details': details,
        'form': form,
        'participants': participants,
    }
    return render(request, 'cooperatives/detail_formation.html', context)

#Parcelle Json
# def my_parcelles(request):
#     parcelles = Parcelle.objects.all()
#     parcelles_list = serializers.serialize('json', parcelles)
#     return HttpResponse(parcelles_list, content_type="text/json-comment-filtered")

# class ParcellesView(View):
#     def get(self, request, *args, **kwargs):
#         if request.is_ajax():
#             parcelles = Producteur.objects.all()
#             parcelles_serializers = serializers.serialize('json', parcelles)
#             return JsonResponse(parcelles_serializers, safe=False)
#         return JsonResponse({'message': 'Erreure Lors du Chargement.....'})
    # parcelles = Parcelle.objects.all()
    # parcelles_list = serializers.serialize('json', parcelles)
    # return HttpResponse(parcelles_list, content_type="text/json-comment-filtered")

# DJango Serializer Views#

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
#Export PARCELLES to PDF
@login_required(login_url='connexion')
def export_prods_to_pdf(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    template_path = 'cooperatives/producteurs_pdf.html'
    context = {
        'cooperative':cooperative,
        'producteurs':producteurs,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste Producteur.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response


def export_parcelles_to_pdf(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    template_path = 'cooperatives/new_parcelles_pdf.html'
    context = {
        'cooperative': cooperative,
        'parcelles': parcelles,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste Producteur.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response

@csrf_exempt
def parcelle_list(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    if request.method == 'GET':
        parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
        parcelles_serializers = serializers.serialize('json', parcelles)
        return JsonResponse(parcelles_serializers, safe=False)

class ParcellesMapView(TemplateView):

    template_name = "map.html"

    def get_context_data(self, **kwargs):
        """Return the view context data."""
        context = super().get_context_data(**kwargs)
        context["parcelles_coop"] = json.loads(serialize("geojson", Parcelle.objects.all()))
        # parcelles_serializers = serializers.serialize('json', parcelles)
        # context["parcelles"] = json.loads(serialize("geojson", Parcelle.objects.all()))
        return context

class ReceptionView(View):
    def get(self, request, *args, **kwargs):
        cooperative = Cooperative.objects.get(user_id=request.user.id)
        parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
        parcelle_list = []
        for parcelle in parcelles:
        #     sub_category = SubCategories.objects.filter(is_active=1, category_id=category.id)
            parcelle_list.append({"parcelle": parcelle})

        # merchant_users = MerchantUser.objects.filter(auth_user_id__is_active=True)
        especes_plants = Espece.objects.all()
        context = {
            "parcelles": parcelles,
            "especes_plants" : especes_plants,
        }
        return render(self.request, "cooperatives/planting_create.html", context)


class AddPlantingView(View):
    def get(self, request, *args, **kwargs):
        cooperative = Cooperative.objects.get(user_id=request.user.id)
        parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
        parcelle_list = []
        for parcelle in parcelles:
            parcelle_list.append({"parcelle": parcelle})

        # merchant_users = MerchantUser.objects.filter(auth_user_id__is_active=True)
        especes = Espece.objects.all()
        campagnes = Campagne.objects.all()
        projets = Projet.objects.all()
        plantings = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative)
        context = {
            'cooperative': cooperative,
            "parcelles": parcelles,
            "campagnes" : campagnes,
            "projets" : projets,
            "especes" : especes,
            "plantings" : plantings,
        }
        return render(self.request, "cooperatives/plantings.html", context)

    def post(self, request, *args, **kwargs):
        cooperative = request.POST.get('cooperative')
        date = request.POST.get("date")
        nb_plant_exitant = request.POST.get("nb_plant_exitant")
        plant_recus = request.POST.get("plant_recus")
        # details = request.POST.get("details")
        campagne = request.POST.get("campagne")
        parcelle = request.POST.get("parcelle")
        projet = request.POST.get("projet")
        espece_list = request.POST.get("espece")
        nb_plante_liste = request.POST.getlist("nb_plante[]")

        parcelle_obj = Parcelle.objects.get(id=parcelle)
        campagne_obj = Campagne.objects.get(id=campagne)
        projet_obj = Projet.objects.get(id=projet)
        plant_total_obj = nb_plant_exitant + plant_recus

        planting = Planting(
            parcelle=parcelle_obj,
            campagne=campagne_obj,
            projet=projet_obj,
            nb_plant_exitant=nb_plant_exitant,
            plant_recus=plant_recus,
            date=date,
            # plant_recus = (nb_plant_exitant + plant_recus)
        )
        planting.save()


        # espece_obj = Espece.objects.get(id=espece_list)
        # detail_planting = DetailPlanting(
        #     planting_id=planting,
        #     espece = espece_obj,
        #     nb_plante=nb_plante_liste[i]
        # )
        # detail_planting.save()
        # i = i + 1
        # i = 0
        # # espece_obj = Espece.objects.get(id=espece_list)
        # for e in espece_list:
        #     detail_planting = DetailPlanting(
        #         planting_id=planting,
        #         espece=e,
        #         nb_plante=nb_plante_liste[i]
        #     )
        #     detail_planting.save()
        #     i = i+1
        # return HttpResponse("OK")

# def load_producteurs(request):
#     cooperative = Cooperative.objects.get(user_id=request.user.id)
#     producteurs = Producteur.objects.filter(cooperative_id=cooperative).order_by('nom')
#     parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
#     context = {
#         'producteurs': producteurs,
#         'parcelles': parcelles,
#     }
#     return render(request, 'cooperative/select.html', context)

def CoopPlantings(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    # parcelles = cooperative.parcelles_set.all()
    parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    # especes = Espece.objects.all()
    campagnes = Campagne.objects.all()
    projets = Projet.objects.all()
    plantings = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative)
    plantingForm = PlantingForm()
    if request.method == 'POST':
        plantingForm = PlantingForm(request.POST, request.FILES)
        if plantingForm.is_valid():
            planting = plantingForm.save(commit=False)
            for parcelle in parcelles:
                planting.parcelle_id = parcelle.id
            # for campagne in campagnes:
            #     planting.campagne_id = campagne.id
            # for projet in projets:
            #     planting.projet_id = projet.id
            planting = planting.save()
            print(planting)
            # print(RetraitForm)
            messages.success(request, "Enregistrement effectué avec succès")
            return redirect('cooperatives:CoopPlantings')

    context = {
        'cooperative':cooperative,
        'parcelles':parcelles,
        'plantings':plantings,
        'campagnes':campagnes,
        'projets':projets,
        'plantingForm':plantingForm,
    }
    return render(request, 'cooperatives/plantings.html', context)

def detail_planting(request, id=None):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    instance = get_object_or_404(Planting, id=id)
    Details_Planting = DetailPlanting.objects.filter(planting_id=instance)
    Monitorings = Monitoring.objects.filter(planting_id=instance)

    monitoringForm = MonitoringForm()
    detailPlantingForm = DetailPlantingForm()

    if request.method == 'POST':

        monitoringForm = MonitoringForm(request.POST, request.FILES)
        detailPlantingForm = DetailPlantingForm(request.POST, request.FILES)

        if monitoringForm.is_valid():
            monitoring = monitoringForm.save(commit=False)
            monitoring.planting_id = instance.id
            monitoring = monitoring.save()
            print(monitoring)
            messages.success(request, "Enregistrement effectué avec succès")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return HttpResponse("Enregistrement effectué avec succès")

        elif detailPlantingForm.is_valid():
            detail = detailPlantingForm.save(commit=False)
            detail.planting_id = instance.id
            detail = detail.save()
            print(detail)
            messages.success(request, "Enregistrement effectué avec succès")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return redirect('cooperatives:suivi_planting', kwargs={'cooperatives:suivi_planting': instance.pk})
            # return HttpResponse("Enregistrement effectué avec succès")
        else:
            pass


    context = {
        'cooperative':cooperative,
        'instance':instance,
        'monitoringForm':monitoringForm,
        'detailPlantingForm':detailPlantingForm,
        'Details_Planting':Details_Planting,
        'Monitorings':Monitorings,
    }
    return render(request, 'cooperatives/detail_planting.html', context)


from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import DetailPlantingFormSet
from .models import Planting


class PlantingList(ListView):
    model = Planting
    template_name = "cooperatives/plantings.html"


# class PlantingCreate(CreateView):
#     model = Planting
#     fields = [
#         "parcelle",
#         "nb_plant_exitant",
#         "plant_recus",
#         "campagne",
#         "projet",
#         "date",
#         "date",
#         "details",
#     ]
#
#
# class PlantingDetailsCreate(CreateView):
#     model = Planting
#     fields = [
#         "parcelle",
#         "nb_plant_exitant",
#         "plant_recus",
#         "campagne",
#         "projet",
#         "date",
#         "date",
#         "details",
#     ]
#     success_url = reverse_lazy('add_planting')
#
#     def get_context_data(self, **kwargs):
#         data = super(PlantingDetailsCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['detailsplanting'] = DetailPlantingFormSet(self.request.POST)
#         else:
#             data['detailsplanting'] = DetailPlantingFormSet()
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         detailsplanting = context['detailsplanting']
#         with transaction.atomic():
#             self.object = form.save()
#
#             if detailsplanting.is_valid():
#                 detailsplanting.instance = self.object
#                 detailsplanting.save()
#         return super(PlantingDetailsCreate, self).form_valid(form)


# class ProfileUpdate(UpdateView):
#     model = Profile
#     success_url = '/'
#     fields = ['first_name', 'last_name']
#
#
# class ProfileFamilyMemberUpdate(UpdateView):
#     model = Profile
#     fields = ['first_name', 'last_name']
#     success_url = reverse_lazy('profile-list')
#
#     def get_context_data(self, **kwargs):
#         data = super(ProfileFamilyMemberUpdate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['familymembers'] = FamilyMemberFormSet(self.request.POST, instance=self.object)
#         else:
#             data['familymembers'] = FamilyMemberFormSet(instance=self.object)
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         familymembers = context['familymembers']
#         with transaction.atomic():
#             self.object = form.save()
#
#             if familymembers.is_valid():
#                 familymembers.instance = self.object
#                 familymembers.save()
#         return super(ProfileFamilyMemberUpdate, self).form_valid(form)


# class PlantingDelete(DeleteView):
#     model = Planting
#     success_url = reverse_lazy('add_planting')


def folium_map(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)

    m = folium.Map(
        location=[5.34939, -4.01705],
        zoom_start=6
    )
    marker_cluster = MarkerCluster().add_to(m)

    map1 = raster_layers.TileLayer(tiles="CartoDB Dark_Matter").add_to(m)
    map2 = raster_layers.TileLayer(tiles="CartoDB Positron").add_to(m)
    map3 = raster_layers.TileLayer(tiles="Stamen Terrain").add_to(m)
    map4 = raster_layers.TileLayer(tiles="Stamen Toner").add_to(m)
    map5 = raster_layers.TileLayer(tiles="Stamen Watercolor").add_to(m)
    folium.LayerControl().add_to(m)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    df = read_frame(parcelles,
                        fieldnames=
                        [
                            'code',
                            'producteur',
                            'sous_section',
                            'acquisition',
                            'latitude',
                            'longitude',
                            'superficie',
                            'culture',
                            'certification',
                        ]
                    )
    # print(df)
    for (index, row) in df.iterrows():
        folium.Marker(
            location=[
                row.loc['latitude'],
                row.loc['longitude']
            ],
           # my_string='CODE: {}, PRODUCTEUR: {}, SECTION: {}, CERTIFICATION: {}, CULTURE: {}, SUPERFICIE: {}'.format(code,),
            # Popup(my_string),
            popup=[
                row.loc['code'],
                row.loc['producteur'],
                row.loc['certification'],
                row.loc['superficie'],
                row.loc['culture'],
                # 'producteur',
                # 'code',
                # 'certification',
                # 'culture',
                # 'superficie',
                # 'CODE' : 'code',
                # 'PRODUCTUER' : 'producteur',
                # 'SOUS SECTION' : 'sous_section',
                # 'CERTIFICATION' : 'certification',
                # 'CULTURE' : 'culture',
                # 'SUPERFICIE' : 'superficie',
            ],
            icon=folium.Icon(color="green", icon="ok-sign"),
        ).add_to(marker_cluster)
    plugins.Fullscreen().add_to(m)
    plugins.DualMap().add_to(m)
    # plugins.MarkerCluster.add_to()
    m = m._repr_html_()

    context = {
        "m":m
    }
    return render(request, "cooperatives/folium_map.html", context)

def folium_palntings_map(request):
    cooperative = Cooperative.objects.get(user_id=request.user.id)
    m = folium.Map(
        location=[5.34939, -4.01705],zoom_start=6,
    )
    marker_cluster = MarkerCluster().add_to(m)

    map1 = raster_layers.TileLayer(tiles="CartoDB Dark_Matter").add_to(m)
    map2 = raster_layers.TileLayer(tiles="CartoDB Positron").add_to(m)
    map3 = raster_layers.TileLayer(tiles="Stamen Terrain").add_to(m)
    map4 = raster_layers.TileLayer(tiles="Stamen Toner").add_to(m)
    map5 = raster_layers.TileLayer(tiles="Stamen Watercolor").add_to(m)
    folium.LayerControl().add_to(m)
    plantings = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative)
    parcelles = Parcelle.objects.filter(roducteur__cooperative_id=cooperative)

    df1 = read_frame(parcelles,
        fieldnames=
        [
            'code',
            'producteur',
            'latitude',
            'longitude',

        ]
    )
    df = read_frame(plantings,
        fieldnames=
        [
            'planting',
            'espece',
            'nb_plante',
            'add_le'
        ]
    )
    print(df)
    html = df.to_html(
        classes="table table-striped table-hover table-condensed table-responsive"
    )

    # print(df)
    for (index, row) in df1.iterrows():
        folium.Marker(
            location=[
                row.loc['latitude'],
                row.loc['longitude']
            ],
            popup=folium.Popup(html),
            icon=folium.Icon(color="green", icon="ok-sign"),
        ).add_to(marker_cluster)
    plugins.Fullscreen().add_to(m)
    m = m._repr_html_()

    context = {
        "m":m
    }
    return render(request, "cooperatives/folium_planting_map.html", context)


@api_view(['GET'])
def getParcelleCoop(request, pk=None):
    cooperative = Cooperative.objects.get(id=pk)
    # cooperative = Cooperative.objects.get(user_id=request.user.id)
    parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    serializer = ParcelleSerializer(parcelles, many=False)
    # serializer = CooperativeSerliazer(cooperative, many=False)
    return Response(serializer.data)



#parcelle par cooperative sur la carte

@api_view(['GET'])
def map_by_cooperative(request):
    coop_connect = Cooperative.objects.get(user_id=request.user.id)
    sections  = Section.objects.filter(cooperative_id = coop_connect.id)
    context = {
        "coop_connect":coop_connect,
        "sections": sections
    }

    return render(request, 'cooperatives/usercoop/coop_connect_carte.html',context)

