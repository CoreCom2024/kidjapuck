from django.contrib import admin
from .models import Booking

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "start_date", "end_date", "guests", "status", "total_price")
    list_filter = ("status", "start_date")
    search_fields = ("room__name",)
    actions = ["admin_mark_confirmed", "admin_mark_cancelled"]

    def admin_mark_confirmed(self, request, queryset):
        queryset.update(status="confirmed")
    admin_mark_confirmed.short_description = "Mark selected as CONFIRMED"

    def admin_mark_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
    admin_mark_cancelled.short_description = "Mark selected as CANCELLED"