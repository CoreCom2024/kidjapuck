from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import timedelta


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
    
    def get_guest_price(self, guests:int):
        return self.guest_prices.filter(guests=guests).values_list("price", flat=True).first()
    
    def _is_weekend(self, day):
        return day.weekday() >= 5
    
    def _active_rules_for_day(self, day):
        qs = self.price_rules.filter(start_date__lte=day, end_date__gte=day)
        filtered = []
        for r in qs:
            if r.weekday_only and self._is_weekend(day):
                continue
            if r.weekend_only and (not self._is_weekend(day)):
                continue
            filtered.append(r)
        return filtered
    
    def calc_total_price(self, start_date, end_date, guests:int):
        """
        คำนวณ 'ราคารวม' สำหรับช่วงคืน [start_date, end_date) ตามจำนวนผู้เข้าพัก
        - base = RoomGuestPrice ที่ตรงกับ guests
        - Rule แบบ ADD_FIXED_PER_GUEST: บวก/ลบ (amount * guests) ต่อคืน
        - Rule แบบ PERCENT: บวก/ลบ ตามเปอร์เซ็นต์ของราคาหลังปรับล่าสุดต่อคืน
        """
        
        if not start_date or not end_date or start_date >= end_date:
            return None
        
        base = self.get_guest_price(guests)
        if base is None:
            return None
        
        day = start_date
        total = Decimal("0.00")
        while day < end_date:
            nightly = Decimal(base)

            for rule in self._active_rules_for_day(day):
                if rule.mode == RoomPriceRule.Mode.ADD_FIXED_PER_GUEST:
                    nightly = nightly + (Decimal(rule.amount) * Decimal(guests))
                elif rule.mode == RoomPriceRule.Mode.PERCENT:
                    nightly = nightly + (nightly * Decimal(rule.percent) / Decimal("100"))
            
            if nightly < 0:
                nightly = Decimal("0.00")

            total += nightly
            day += timedelta(days=1)

        return total

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
    

