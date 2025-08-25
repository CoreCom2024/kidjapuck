from django.db import models
from django.contrib.auth.models import User

# Create your models here.
    
class CreditAccount(models.Model):
    partner = models.OneToOneField("properties.Partner", on_delete=models.CASCADE, related_name="credit")
    balance = models.IntegerField(default=0)

class CreditTransaction(models.Model):
    TOPUP = "TOPUP"
    USAGE = "USAGE"
    TYPES = [(TOPUP, "Topup"), (USAGE, "Usage")]
    account = models.ForeignKey(CreditAccount, on_delete=models.CASCADE, related_name="tx")
    type = models.CharField(max_length=10, choices=TYPES)
    amount = models.IntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 