from django.contrib import admin
from .models import Booking
from django.db import transaction

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "start_date", "end_date", "guests", "status", "total_price")
    list_filter = ("status", "start_date")
    search_fields = ("room__name",)
    actions = ["admin_mark_confirmed", "admin_mark_cancelled"]

    def admin_mark_confirmed(self, request, queryset):
            updated = 0
            for b in queryset.exclude(status="confirmed").iterator():
                b.status = "confirmed"
                b.save(update_fields=["status"])   # post_save จะยิง signal
                updated += 1
            self.message_user(request, f"Confirmed {updated} booking(s).")
    admin_mark_confirmed.short_description = "Mark selected as CONFIRMED"

    def admin_mark_cancelled(self, request, queryset):
            updated = 0
            for b in queryset.exclude(status="cancelled").iterator():
                b.status = "cancelled"
                b.save(update_fields=["status"])   # post_save จะยิง signal
                updated += 1
            self.message_user(request, f"Cancelled {updated} booking(s).")
    admin_mark_cancelled.short_description = "Mark selected as CANCELLED"