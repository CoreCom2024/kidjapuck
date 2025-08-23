from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Room
from bookings.models import Booking
from datetime import date
from django.utils.dateparse import parse_date

# Create your views here.

def search(request):
    start_str = request.GET.get("start_date")
    end_str   = request.GET.get("end_date")
    guests    = int(request.GET.get("guests", 1))

    start = parse_date(start_str) if start_str else None
    end   = parse_date(end_str)   if end_str   else None

    rooms = (Room.objects
             .filter(is_active=True, property__is_approved=True, max_guests__gte=guests)
             .prefetch_related("guest_prices", "price_rules", "block_dates"))

    if start and end:
        # กันชนกับ Booking ที่ทับช่วงวัน
        conflict_bookings = (Booking.objects
            .filter(status__in=["pending_payment", "await_partner_confirm", "confirmed"])
            .filter(Q(start_date__lt=end) & Q(end_date__gt=start))
            .values_list("room_id", flat=True))

        # กันชนกับช่วงปิดห้อง
        conflict_blocks = (Room.objects
            .filter(block_dates__start_date__lt=end, block_dates__end_date__gt=start)
            .values_list("id", flat=True))

        rooms = rooms.exclude(id__in=conflict_bookings).exclude(id__in=conflict_blocks)

        # คิดราคารวมและผูกไว้กับอ็อบเจ็กต์ room เพื่อให้เทมเพลตเรียกใช้ง่าย
        for r in rooms:
            r.total_price = r.calc_total_price(start, end, guests)

        if start and end:
            nights = (end - start).days
            for r in rooms:
                r.avg_price = (r.total_price / nights) if (getattr(r, "total_price", None) and nights > 0) else None
        else:
            nights = 0

    nights = (end - start).days if (start and end) else 0

    context = {
        "rooms": rooms,
        "start_date": start,
        "end_date": end,
        "guests": guests,
        "nights": nights,
    }
    return render(request, "properties/search_results.html", context)

def room_detail(request, room_id):
    start_str = request.GET.get("start_date")
    end_str = request.GET.get("end_date")
    guests = int(request.GET.get("guests", 1))

    start = parse_date(start_str) if start_str else None
    end = parse_date(end_str) if end_str else None

    room = (Room.objects
            .prefetch_related("images", "guest_prices", "price_rules", "block_dates")
            .select_related("property")
            .get(pk=room_id)     
    )

    total_price = None
    nights = 0
    if start and end:
        nights = (end - start).days
        total_price = room.calc_total_price(start, end, guests)

        has_conglict = False
        if nights > 0:
            conflict_booking = Booking.objects.filter(
                room=room,
                status__in=["pending_payment", "await_partner_confirm", "confirmed"],
                
            ).filter(Q(start_date__lt=end) & Q(end_date__gt=start)).exists()

            conflict_block = room.block_dates.filter(
                start_date__lt=end, end_date__gt=start
            ).exists()
            has_conflict = conflict_booking or conflict_block
        else:
            has_conflict = False

        context = {
            "room": room,
            "start_date": start,
            "end_date": end,
            "guests": guests,
            "nights": nights,
            "total_price": total_price,
            "has_conflict": has_conflict,
            "avg_price": (total_price / nights) if (total_price and nights > 0) else None,
        }

        return render(request, "properties/room_detail.html", context)