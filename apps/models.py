from django.db import models


class App(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    APP_STATES = (
        ('I', 'Installed'),
        ('P', 'Installing'),
        ('F', 'Failed'),
        ('U', 'Not installed'),
    )
    state = models.CharField(max_length=1, choices=APP_STATES)


class Job(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    pid = models.PositiveIntegerField()
    hash = models.CharField(max_length=100)
    JOB_STATES = (
        ('R', 'Running'),
        ('C', 'Completed'),
    )
    state = models.CharField(max_length=1, choices=JOB_STATES)
