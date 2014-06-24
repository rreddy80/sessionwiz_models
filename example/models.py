from django.db import models

# Create your models here.

class Model1(models.Model):
    subject = models.CharField(max_length=100)
    sender = models.EmailField(blank=True)
    message = models.CharField(max_length=100, blank=True)
    amt_paid = models.DecimalField(max_digits=9, decimal_places=2,
                                   default=0, blank=True)
    
    def __unicode__(self):
        return self.subject


class Model2(models.Model):
    message2 = models.CharField(max_length=100)

    def __unicode__(self):
        return self.message2


class Model3(models.Model):
    amt_paid2 = models.DecimalField(max_digits=9, decimal_places=2)

    def __unicode__(self):
        return str(self.amt_paid2)

class statement_progress(models.Model):
    statement = models.ForeignKey(Model1)
    current_step = models.IntegerField()

    def __unicode__(self):
        return str(self.statement)
