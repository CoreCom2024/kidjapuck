from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

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
    class Mode(models.TextChoices):
        ADD_FIXED_PER_GUEST = "ADD_FIXED_PER_GUEST", "add fixed per guest"
        PERCENT = "PERCENT", "add percent from base"
    name = models.CharField(max_length=255, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="price_rules")
    start_date = models.DateField()
    end_date = models.DateField()
    weekday_only = models.BooleanField(default=False)
    weekend_only = models.BooleanField(default=False)
    
    mode = models.CharField(max_length=50, choices=Mode.choices, default=Mode.ADD_FIXED_PER_GUEST)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percent = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        validators=[MinValueValidator(-90), MaxValueValidator(300)],
        help_text="10.00 = +10%, -15.00 = -15% "
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.weekday_only and self.weekend_only:
            raise ValidationError("กรุณาเลือก อย่างเดียว")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("end date ต้องอยู่หลัง start date")

class RoomGuestPrice(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="guest_prices")
    guests = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.room} - {self.guests}"

class RoomBlockDate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="block_dates")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    

