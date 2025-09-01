from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Booking

# Create your views here.
def partner_confirm(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    if request.method == "POST":
        booking.status = "confirmed"
        booking.save(update_fields = ["status"])
        messages.success(request, f"Booking #{booking.id} confirmed.")
        return redirect("partner_dashboard")
    
    context = {
        "booking": booking,
    }
    return render(request, "bookings/partner_confirm.html", context)