from django.contrib import admin
from .models import Booking

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "start_date", "end_date", "guests", "status", "total_price")
    list_filter = ("status", "start_date")
    search_fields = ("room__name",)