from django.db import models


class Apps(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    APP_STATES = (
        ('I', 'Installed'),
        ('P', 'Installing'),
        ('F', 'Failed'),
    )
    state = models.CharField(max_length=1, choices=APP_STATES)
