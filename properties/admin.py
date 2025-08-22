from django.contrib import admin
from .models import (Partner,
    Property, Room, RoomImage,
    RoomPriceRule, RoomGuestPrice, RoomBlockDate,                 
    )

# Register your models here.
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "is_active")
    search_fields = ("display_name", "user__username")

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "is_approved")
    list_filter = ("is_approved",)

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "property", "max_guests", "is_active")
    list_filter = ("is_active", "property__is_approved")
    inlines = [RoomImageInline]

@admin.register(RoomGuestPrice)
class RoomGuestPriceAdmin(admin.ModelAdmin):
    list_display = ("room", "guests", "price")

@admin.register(RoomPriceRule)
class RoomPriceRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "room")

@admin.register(RoomBlockDate)
class RoomBlockDateAdmin(admin.ModelAdmin):
    list_display = ("room", "start_date", "end_date")
