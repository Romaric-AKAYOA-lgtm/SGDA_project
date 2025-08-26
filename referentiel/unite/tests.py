from django.test import TestCase

from referentiel.unite.models import Unite


# Create your tests here.

# Direction
direction = Unite.objects.create(designation="Direction Générale")

# Service (rattaché à la Direction)
service = Unite.objects.create(designation="Service Informatique", unite_parent=direction)

# Division (rattachée au Service)
division = Unite.objects.create(designation="Division Réseaux", unite_parent=service)

# Section (rattachée à la Division)
section = Unite.objects.create(designation="Section Support", unite_parent=division)
