from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class BankAccount(models.Model):
    account_no=models.CharField(max_length=100, null=True, blank=True)
    card_number = models.CharField(max_length=100, blank=True, null=True)
    pin_number = models.CharField(max_length=50, blank=True, null=True)
    amount=models.FloatField(null=True, blank=True)
    card_type=models.CharField(max_length=100)
    card_holder=models.CharField(max_length=100)
    expiry_month=models.IntegerField()
    expiry_year=models.IntegerField()
    currency=models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.card_number

