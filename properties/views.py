from django.shortcuts import render
from django.db.models import Q
from .models import Room
from bookings.models import Booking

# Create your views here.
def search(request):
    start = request.GET.get("start_date")
    end = request.GET.get("end_date")
    guests = int(request.GET.get("guests", 1))

    rooms = Room.objects.filter(is_active=True, property__is_approved=True, max_guests__gte=guests )

    if start and end:
        conflict_bookings = Booking.objects.filter(
            status__in=["pending_payment", "await_partner_confirm", "confirmed"]

        ).filter(
            Q(start_date__lt=end) & Q(end_date__gt=start)
        ).values_list("room_id", flat=True)

        conflict_blocks = Room.objects.filter(
            block_dates__start_date__lt=end,
            block_dates__end_date__gt=start,
        ).values_list("id", flat=True)

        rooms = rooms.exclude(id__in=conflict_bookings).exclude(id__in=conflict_blocks)

    context = {
        "rooms": rooms,
    }

    return render(request, "properties/search_results.html", context )