import datetime
import os
import time

from django.contrib.auth.models import User
from django.db import models

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from parametres.models import Espece, Campagne, Region, Origine, Sous_Prefecture, Cooperative


def producteurs_documents(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "Producteurs/Documents/" + self.code

def producteurs_images(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "Producteurs/Images/" + self.code + ".jpeg"

def upload_logo_site(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "logos/" + self.user.username + ".jpeg"

TYPE_PRODUCTEUR = (
    ('membre', "MEMBRE"),
    ('usager', "USAGER"),
)

NATURE_DOC = (
    ('AUCUN', 'AUCUN'),
    ('ATTESTATION', 'ATTESTATION'),
    ('CNI', 'CNI'),
    ('PASSEPORT', 'PASSEPORT'),
    ('SEJOUR', 'CARTE DE SEJOUR'),
    ('CONSULAIRE', 'CARTE CONSULAIRE'),
)

type_parcelle = (
    ("AGROFORESTERIE", "AGROFORESTERIE"),
    ("COMMUNAUTAIRE", "COMMUNAUTAIRE"),
    ("FORET_CLASSEE", "FORET CLASSEE"),
    ("INDIVIDUELLE", "INDIVIDUELLE"),
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
    ('autre', 'AUTRE'),
)

GENRE = (
    ('H', "HOMME"),
    ('F', "FEMME"),
)

ACQUISITION = (
    ('heritage', 'HERITAGE'),
    ('achat', 'ACHAT'),
    ('autres', 'AUTRES'),
)

CULTURE_ASSOCIEE = (
    ("banane", "BANANE"),
    ("coton", "COTON"),
    ("igname", "IGNAME"),
    ("mais", "MAIS"),
    ("manioc", "MANIOC"),
    ("riz", "RIZ"),
)

class Projet(models.Model):
    code = models.CharField(max_length=3, verbose_name="CODE PROJET")
    libelle = models.CharField(max_length=50, verbose_name="DESIGNATION")
    chef = models.CharField(max_length=50, verbose_name="CHEF PROJET")
    add_le = models.DateTimeField(auto_now_add=True)
    update_le = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return ("%s") %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.code = self.code.upper()
        self.libelle = self.libelle.upper()
        self.chef = self.chef.upper()
        super(Projet, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "PROJETS"
        verbose_name = "projet"
        ordering = ["libelle"]

class Section(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="section")
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=250)
    responsable = models.CharField(max_length=250, blank=True, null=True)
    contacts = models.CharField(max_length=50, blank=True, null=True)
    add_le = models.DateTimeField(auto_now_add=True)
    update_le = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return '%s' % (self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        if self.responsable:
            self.responsable = self.responsable.upper()
        super(Section, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "SECTIONS"
        verbose_name = "section"
        ordering = ["libelle"]

class Parcelle(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="parcelles")
    type = models.CharField(max_length=255, choices=type_parcelle)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="projet_parcelle")
    code_parcelle = models.CharField(max_length=25)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True, null=True)
    proprietaire = models.CharField(max_length=255)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    superficie = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    localite = models.CharField(max_length=255, blank=True, null=True)
    culture = models.CharField(max_length=50, verbose_name="CULTURE", choices=CULTURE, blank=True, null=True)
    culture_associee = models.CharField(max_length=50, verbose_name="CULTURE ASSOCIEE", choices=CULTURE_ASSOCIEE, blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return ("%s - %s") %(self.proprietaire, self.code_parcelle)

    def coordonnees(self):
        return str(self.longitude) + ' , ' + str(self.latitude)

    class Meta:
        verbose_name_plural = "PARCELLES"
        verbose_name = "parcelle"

class Planting(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='parcelles')
    nb_plant_exitant = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS EXISTANTS")
    plant_recus = models.PositiveIntegerField(default=0, verbose_name="NOMBRE DE PLANTS RECUS")
    plant_total = models.PositiveIntegerField(default=0, verbose_name="NOMBRE TOTAL DE PLANTS")
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name='campagne_parif')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='planting_parif')
    date = models.DateTimeField(default=now)

    objects = models.Manager()

    # def get_absolute_url(self):
    #     return reverse('cooperatives:suivi_planting', kwargs={'pk': self.pk})

    def __str__(self):
        return 'Reception de %s plants sur %s' % (self.plant_total, self.parcelle)

    def save(self, force_insert=False, force_update=False):
        self.plant_total = (self.nb_plant_exitant) + (self.plant_recus)
        super(Planting, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "PLANTINGS"
        verbose_name = "planting"

class DetailPlanting(models.Model):
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE, related_name='plantings')
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE, related_name='epece_parif')
    nb_plante = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS PLANTE/ESPECE")
    add_le = models.DateTimeField(auto_now_add=True)
    update_le = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "DETAILS PLANTINGS"
        verbose_name = "details planting"

class Monitoring(models.Model):
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE)
    mort = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS MORTS")
    remplace = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS REMPLACES")
    mature = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS VIVANTS")
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE, default=1, related_name="monitorings")
    observation = models.TextField(blank=True, null=True)
    date = models.DateField()
    add_le = models.DateTimeField(auto_now_add=True)
    update_le = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "MONITORINGS"
        verbose_name = "monitoring"
# Create your models here.
