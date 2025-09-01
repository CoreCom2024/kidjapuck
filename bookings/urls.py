from django.urls import path
from .views import partner_confirm

urlpatterns = [
    path("<int:booking_id>/confirm/", partner_confirm, name="booking_partner_confirm"),
]