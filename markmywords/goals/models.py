from django.db import models

# Create your models here.
class Goal(models.Model):
	distance = models.DecimalField(max_digits=8, decimal_places=2)
	created_date = models.DateTimeField()
	end_date = models.DateTimeField()
	money = models.DecimalField(max_digits=8, decimal_places=2)
	charity_ppid = models.PositiveIntegerField()
