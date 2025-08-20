from django.db import models
from django.contrib.auth import get_user_model
from properties.models import Room
User = get_user_model()

# Create your models here.
class Booking(models.Model):
    STATUS = [
        ("pending_payment", "Pending Payment"),
        ("await_partner_confirm", "Await Partner Confirm"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS, default="pending_payment")
    payment_slip = models.ImageField(upload_to="payment_slip/", blank=True, null=True)
    is_sms_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]