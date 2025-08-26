from django.db import models

class Unite(models.Model):
    designation = models.CharField(max_length=20, unique=True)
    unite_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_unites'
    )

    def __str__(self):
        return self.designation
