# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import datetime

from django.db.models import Sum, Count
from django.http import request
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from sorl.thumbnail import get_thumbnail
from clients.models import Client
from parametres.models import Region, Projet, Activite, Origine, Sous_Prefecture, Campagne, Espece, Cooperative


def producteurs_images(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "producteurs/images/" + self.code + ".jpeg"

def producteurs_documents(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "producteurs/documents/" + self.code

def upload_logo_site(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "logos/" + self.code + ".jpeg"

TYPE_PRODUCTEUR = (
    ('MEMBRE', "MEMBRE"),
    ('USAGER', "USAGER"),
)

NATURE_DOC = (
    ('AUCUN', 'AUCUN'),
    ('ATTESTATION', 'ATTESTATION'),
    ('CNI', 'CNI'),
    ('PASSEPORT', 'PASSEPORT'),
    ('SEJOUR', 'CARTE DE SEJOUR'),
    ('CONSULAIRE', 'CARTE CONSULAIRE'),
)

CULTURE = (
    ('ANACARDE', 'ANACARDE'),
    ('CACAO', 'CACAO'),
    ('CAFE', 'CAFE'),
    ('COTON', 'COTON'),
    ('HEVEA', 'HEVEA'),
    ('PALMIER', 'PALMIER A HUILE'),
    ('SOJA', 'SOJA'),
    ('AUTRE', 'AUTRE'),
)

CERTIFICATION = (
    ('UTZ', 'UTZ'),
    ('RA', 'RA'),
    ('BIO', 'BIO'),
    ('PROJET', 'PROJET'),
    ('AUTRE', 'AUTRE'),
)

GENRE = (
    ('H', "HOMME"),
    ('F', "FEMME"),
)

ACQUISITION = (
    ('HERITAGE', 'HERITAGE'),
    ('ACHAT', 'ACHAT'),
    ('AUTRES', 'AUTRES'),
)

MODEL_AGRO = (
    ("AUTOUR", "AUTOUR"),
    ("CENTRE", "AUTOUR & CENTRE"),
)

class Section(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="sections")
    libelle = models.CharField(max_length=250)
    responsable = models.CharField(max_length=250, blank=True, null=True)
    contacts = models.CharField(max_length=50, blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return '%s' %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        if self.responsable:
            self.responsable = self.responsable.upper()
        super(Section, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "SECTIONS"
        verbose_name = "section"
        ordering = ["libelle"]

class Sous_Section(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=250)
    responsable = models.CharField(max_length=250, blank=True, null=True)
    contacts = models.CharField(max_length=50, blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return '%s' %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        if self.responsable:
            self.responsable = self.responsable.upper()
        super(Sous_Section, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "SOUS SECTIONS"
        verbose_name = "sous section"
        ordering = ["libelle"]

class Producteur(models.Model):
    code = models.CharField(max_length=150, blank=True, null=True, verbose_name='CODE PRODUCTEUR')
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name='producteurs')
    origine = models.ForeignKey(Origine, on_delete=models.CASCADE, related_name='producteurs', default=1)
    sous_prefecture = models.ForeignKey(Sous_Prefecture, on_delete=models.SET_NULL, blank=True, null=True, related_name='producteurs')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='producteurs')
    sous_section = models.ForeignKey(Sous_Section, related_name="sous_section", on_delete=models.SET_NULL, blank=True, null=True)
    type_producteur = models.CharField(max_length=50, verbose_name="TYPE PRODUCTEUR", choices=TYPE_PRODUCTEUR, default="MEMBRE")
    genre = models.CharField(max_length=2, choices=GENRE, default="H")
    nom = models.CharField(max_length=250, blank=True, null=True, verbose_name="Nom et prénoms")
    dob = models.CharField(max_length=50, blank=True, null=True, verbose_name="Date/Année de Naissance")
    # dob = models.DateField(blank=True, null=True, verbose_name="date de Naissance")
    contacts = models.CharField(max_length=50, blank=True, null=True)
    localite = models.CharField(max_length=100, blank=True, null=True)
    nb_enfant = models.PositiveIntegerField(default=0, null=True, blank=True)
    nb_parcelle = models.PositiveIntegerField(default=0)
    image = models.ImageField(verbose_name="Logo", upload_to=producteurs_images, blank=True)
    type_document = models.CharField(max_length=50, verbose_name="TYPE DOCUMENT", choices=NATURE_DOC, default="AUCUN")
    num_document = models.CharField(max_length=150, verbose_name="N° PIECE", null=True, blank=True)
    document = models.FileField(verbose_name="Documents", upload_to=producteurs_documents, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return '%s' %(self.nom)

    def Producteur(self):
        return '%s - %s' % ( self.code, self.nom)

    def save(self, force_insert=False, force_update=False):
        self.code = self.code.upper()
        super(Producteur, self).save(force_insert, force_update)
    def clean(self):
        if self.type_document != "AUCUN" and self.document == "":
            raise ValidationError('Veuillez Charger le Document Approprié SVP')

    def Photo(self):
        if self.image:
            photoLink = "/media/%s" % self.image
            thumb = mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.image.url)
            return "<img src='%s' />" % thumb.url
        elif self.genre == "H":
            thumb = mark_safe('<img src="127.0.0.1:8000/static/img/logo_homme.jpeg" style="width: 45px; height:45px;" />')
            # thumb = get_thumbnail('127.0.0.1:8000/static/img/logo_home.jpeg', "60x60", crop='center', quality=99)
            return "<img src='%s' />" % thumb
            # return ""
        else:
            thumb = mark_safe('<img src="127.0.0.1:8000/static/img/logo_femme.jpeg" style="width: 45px; height:45px;" />')
            return "<img src='%s' />" % thumb
            # return "127.0.0.1:8000/img/avatar3.png"
            # return "Aucun logo"

    Photo.short_description = "Logo"
    Photo.allow_tags = True

    class Meta:
        verbose_name_plural = "PRODUCTEURS"
        verbose_name = "producteur"
        ordering = ["id"]

class Parcelle(models.Model):
    code = models.CharField(max_length=150, blank=True, null=True, verbose_name='CODE PARCELLE', help_text="LE CODE PARCELLE EST GENERE AUTOMATIQUEMENT")
    producteur = models.ForeignKey(Producteur, related_name='parcelles', on_delete=models.CASCADE)
    acquisition = models.CharField(max_length=50, verbose_name="MODE ACQUISITION", choices=ACQUISITION, default="heritage")
    latitude = models.CharField(max_length=10, null=True, blank=True)
    longitude = models.CharField(max_length=12, null=True, blank=True)
    superficie = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    culture = models.CharField(max_length=50, verbose_name="CULTURE", choices=CULTURE, default="cacao")
    certification = models.CharField(max_length=50, verbose_name="CERTIFICATION", choices=CERTIFICATION, default="utz")
    objects = models.Manager()

    def __str__(self):
        if self.code:
            return "%s - %s" % (self.code, self.producteur)
        else:
            return "%s - %s" % (self.producteur.code, self.producteur)

    def coordonnees(self):
        return str(self.longitude) + ', ' + str(self.latitude)

    class Meta:
        verbose_name_plural = "PARCELLES"
        verbose_name = "parcelle"
        ordering = ["code"]

class Planting(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name="plantings")
    nb_plant_exitant = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS EXISTANTS")
    plant_recus = models.PositiveIntegerField(default=0, verbose_name="NOMBRE DE PLANTS RECUS")
    plant_total = models.PositiveIntegerField(default=0, verbose_name="NOMBRE TOTAL DE PLANTS")
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name="plantings")
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('cooperatives:suivi_planting', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s - (%s) plants reçus' % (self.parcelle.producteur, self.parcelle)

    def save(self, force_insert=False, force_update=False):
        self.plant_total = (self.nb_plant_exitant) + (self.plant_recus)
        super(Planting, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "PLANTINGS"
        verbose_name = "planting"
        ordering = ["parcelle"]

class DetailPlanting(models.Model):
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE)
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE, default=1)
    nb_plante = models.PositiveIntegerField(default=0, verbose_name="QTE recu")
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('cooperatives:suivi_planting',args=[self.planting.id])

    def total_plants(self):
        planting = get_object_or_404(Planting, id=id)
        t_planting = DetailPlanting.objects.filter(planting_id=planting).aggregate(total=Sum('nb_plante'))
        return t_planting

    class Meta:
        verbose_name_plural = "DETAILS PLANTINGS"
        verbose_name = "details planting"

class Monitoring(models.Model):
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE)
    mort = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS MORTS")
    remplace = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS REMPLACES")
    mature = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS VIVANTS")
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE, default=1)
    # nb_plante = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS REMPLACES")
    observation = models.TextField(blank=True, null=True)
    date = models.DateField()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "MONITORINGS PLANTINGS"
        verbose_name = "monitoring planting"


class Formation(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, default=1)
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, default=1)
    formateur = models.CharField(max_length=255, verbose_name="FORMATEUR")
    libelle = models.CharField(max_length=500, verbose_name='INTITULE DE LA FORMATION')
    debut = models.DateField(verbose_name="DATE DEBUT")
    fin = models.DateField(verbose_name="DATE FIN")
    observation = models.TextField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return "%s" %(self.libelle)

    def Duree(self):
        delta = (self.fin - self.debut).days
        return delta - (delta // 7) * 2 #calcul nombrede jours travailler(sans week-end)

    class Meta:
        verbose_name_plural = "FORMATIONS"
        verbose_name = "formation"
        ordering = ["libelle"]

class Detail_Formation(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    participant = models.ManyToManyField(Producteur)
    objects = models.Manager()

    def Participants(self):
        nb_participants = self.participant.all().count()
        return nb_participants

    def __str__(self):
        return "%s" % (self.formation.libelle)

    class Meta:
        verbose_name_plural = "DETAILS FORMATIONS"
        verbose_name = "details formation"
        ordering = ["formation"]

# Create your models here.
