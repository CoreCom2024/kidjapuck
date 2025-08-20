from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Partner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partners")
    display_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.display_name}"
    
class Property(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="properties")
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"
    
class Room(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=255)
    max_guests = models.PositiveIntegerField(default=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.property.name} - {self.name}"
    
class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="room_images/")

class RoomPriceRule(models.Model):
    room = models.ForeignKey(Room, on_delete=models.Case, related_name="price_rules")
    start_date = models.DateField()
    end_date = models.DateField()
    weekday_only = models.BooleanField(default=False)
    weekend_only = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class RoomGuestPrice(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="guest_prices")
    guests = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class RoomBlockDate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="block_dates")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    

