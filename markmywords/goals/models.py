from django.db import models

# Create your models here.
class Goal(models.Model):
	distance = models.DecimalField(max_digits=8, decimal_places=2)
	created_date = models.DateField()
	end_date = models.DateField()
	money = models.DecimalField(max_digits=8, decimal_places=2)
	charity_ppid = models.PositiveIntegerField()
