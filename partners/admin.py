from django.contrib import admin
from .models import (
    CreditAccount, CreditTransaction
)   

# Register your models here.



admin.site.register(CreditAccount)
admin.site.register(CreditTransaction)