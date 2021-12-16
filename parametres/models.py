# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import datetime

from django.urls import reverse
from django.utils.safestring import mark_safe

from clients.models import Client

ANNEES = []
for r in range(2019, (datetime.datetime.now().year+1)):
    ANNEES.append((r,r))

def upload_logo_site(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "logos/" + self.code + ".jpeg"

ETAT = (
    ('en_cours', 'EN COURS'),
    ('suspendu', 'SUSPENDU'),
    ('traite', 'TRAITE'),
)

CULTURE = (
    ('ANACARDE', 'ANACARDE'),
    ('CACAO', 'CACAO'),
    ('CAFE', 'CAFE'),
    ('COTON', 'COTON'),
    ('HEVEA', 'HEVEA'),
    ('PALMIER', 'PALMIER A HUILE'),
)

CERTIFICATION = (
    ('UTZ', 'UTZ'),
    ('RA', 'RA'),
    ('BIO', 'BIO'),
    ('PROJET', 'PROJET'),
)

class Origine(models.Model):
    code = models.CharField(max_length=2, verbose_name="CODE PAYS")
    pays = models.CharField(max_length=255, verbose_name="PAYS")
    objects = models.Manager()

    def __str__(self):
        return "%s" %(self.pays)

    class Meta:
        verbose_name_plural = "ORIGINES"
        verbose_name = "origine"
        ordering = ["pays"]

    def save(self, force_insert=False, force_update=False):
        self.code = self.code.upper()
        self.pays = self.pays.upper()
        super(Origine, self).save(force_insert, force_update)

class Region(models.Model):
    libelle = models.CharField(max_length=250)
    objects = models.Manager()

    def __str__(self):
        return "%s" %(self.libelle)

    class Meta:
        verbose_name_plural = "REGIONS"
        verbose_name = "region"
        ordering = ["libelle"]

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        super(Region, self).save(force_insert, force_update)

class Sous_Prefecture(models.Model):
    libelle = models.CharField(max_length=250)
    objects = models.Manager()

    def __str__(self):
        return "%s" %(self.libelle)

    class Meta:
        verbose_name_plural = "SOUS PREFECTURES"
        verbose_name = "sous prefecture"
        ordering = ["libelle"]

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        super(Sous_Prefecture, self).save(force_insert, force_update)

class Projet_Cat(models.Model):
    libelle = models.CharField(max_length=500, verbose_name="CATEGORIE PROJET")
    objects = models.Manager()

    def __str__(self):
        return "%s" % (self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        super(Projet_Cat, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "CATEGORIES PROJETS"
        verbose_name = "catégorie projet"
        ordering = ["libelle"]

class Projet(models.Model):
    # client = models.ForeignKey(Client, verbose_name="CLIENT", on_delete=models.CASCADE, default=1)
    categorie = models.ForeignKey(Projet_Cat, on_delete=models.CASCADE, verbose_name="CATEGORIE PROJET", default=1)
    sigle = models.CharField(max_length=255)
    titre = models.CharField(max_length=500)
    chef = models.CharField(max_length=255)
    debut = models.DateField()
    fin = models.DateField()
    etat = models.CharField(max_length=50, choices=ETAT)
    objects = models.Manager()

    def __str__(self):
        return "%s - (%s)" %(self.titre, self.categorie.libelle)

    class Meta:
        verbose_name_plural = "PROJETS"
        verbose_name = "projet"
        ordering = ["sigle"]

    def save(self, force_insert=False, force_update=False):
        self.sigle = self.sigle.upper()
        self.titre = self.titre.upper()
        self.chef = self.chef.upper()
        super(Projet, self).save(force_insert, force_update)

class Campagne(models.Model):
    Month_choice = (
        ('JAN', 'JANVIER'),
        ('FEV', 'FEVRIER'),
        ('MAR', 'MARS'),
        ('AVR', 'AVRIL'),
        ('MAI', 'MAI'),
        ('JUN', 'JUIN'),
        ('JUL', 'JUILLET'),
        ('AUG', 'AOUT'),
        ('SEP', 'SEPTEMBRE'),
        ('OCT', 'OCTOBRE'),
        ('NOV', 'NOVEMBRE'),
        ('DEC', 'DECEMBRE'),
    )
    titre = models.CharField(max_length=500, blank=True, null=True, editable=False)
    mois_debut = models.CharField(max_length=50, choices=Month_choice, default="NOV")
    annee_debut = models.IntegerField(verbose_name='Année début', choices=ANNEES, default=datetime.datetime.now().year)
    mois_fin = models.CharField(max_length=50, choices=Month_choice, default="SEP")
    annee_fin = models.IntegerField(verbose_name='Année fin', default=(datetime.datetime.now().year +1))

    class Meta:
        verbose_name_plural = "CAMPAGNES"
        verbose_name = "campagne"
        ordering = ["-titre"]

    def DEBUT(self):
        if self.mois_debut !="" and self.annee_debut !="":
            DEBUT = "%s, %s" %(self.mois_debut, self.annee_debut)
            return DEBUT

    def FIN(self):
        if self.mois_fin !="" and self.annee_fin !="":
            FIN = "%s, %s" %(self.mois_fin, self.annee_fin)
            return FIN

    def save(self, force_insert=False, force_update=False):
        if self.annee_fin =="":
            current_year  = datetime.datetime.now().year
            self.annee_fin = current_year + 1

        if self.mois_debut !="" and self.mois_fin !="" and self.annee_debut !="" and self.annee_fin !="" :
            self.titre = "%s,%s - %s,%s" %(self.mois_debut, self.annee_debut, self.mois_fin, self.annee_fin)
        super(Campagne, self).save(force_insert, force_update)

    def __str__(self):
        return "%s" %(self.titre)

class Prime(models.Model):
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE)
    culture = models.CharField(max_length=150, choices=CULTURE)
    certification = models.CharField(max_length=150, choices=CERTIFICATION)
    prix = models.PositiveIntegerField(default=100, verbose_name="Prix/Kg")
    objects = models.Manager()

    def __str__(self):
        return "%s-%s %s" %(self.culture, self.certification, self.prix)

    class Meta:
        verbose_name_plural = "PRIMES"
        verbose_name = "prime"

class Activite(models.Model):
    libelle = models.CharField(max_length=500, verbose_name="NATURE ACTIVITE")
    objects = models.Manager()

    def __str__(self):
        return '%s' %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        super(Activite, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "ACTIVITES"
        verbose_name = "activite"
        ordering = ["libelle"]

class Cat_Plant(models.Model):
    libelle = models.CharField(max_length=50, verbose_name="Categorie")

    def __str__(self):
        return '%s' %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        super(Cat_Plant, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "CATEGORIES PLANTS"
        verbose_name = "categorie plant"
        ordering = ["libelle"]

class Espece(models.Model):
    categorie = models.ForeignKey(Cat_Plant, on_delete=models.CASCADE)
    accronyme = models.CharField(max_length=250, verbose_name="NOM SCIENTIFIQUE")
    libelle = models.CharField(max_length=250, verbose_name="NOM USUEL")

    def __str__(self):
        return '%s (%s)' %(self.libelle, self.accronyme)

    def save(self, force_insert=False, force_update=False):
        self.accronyme = self.accronyme.upper()
        self.libelle = self.libelle.upper()
        super(Espece, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "ESPECES"
        verbose_name = "espece"
        ordering = ["libelle"]

class Cooperative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cooperatives")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cooperatives")
    siege = models.CharField(max_length=255, verbose_name="SIEGE/LOCALITE", blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="cooperatives")
    projet = models.ManyToManyField(Projet)
    sigle = models.CharField(max_length=500)
    contacts = models.CharField(max_length=50)
    logo = models.ImageField(verbose_name="logo", upload_to=upload_logo_site, blank=True)
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('cooperatives:dashboard', kwargs={"id": self.id})

    def get_projet_values(self):
        ret = ''
        for proj in self.projet.all():
            ret = ret + proj.titre + ','
        return ret[:-1]

    def __str__(self):
        return '%s' %(self.sigle)

    def save(self, force_insert=False, force_update=False):
        self.sigle = self.sigle.upper()
        self.siege = self.siege.upper()
        self.user.last_name = self.user.last_name.upper()
        self.user.first_name = self.user.first_name.upper()
        super(Cooperative, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "COOPERATIVES"
        verbose_name = "cooperative"
        ordering = ["sigle"]

    def Logo(self):
        if self.logo:
            return mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.logo.url)
        else:
            return "Aucun Logo"

    Logo.short_description = 'Logo'
    # Create your models here.

# Create your models here.
