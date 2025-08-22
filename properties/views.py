from django.shortcuts import render
from django.db.models import Q
from .models import Room
from bookings.models import Booking
from datetime import date
from django.utils.dateparse import parse_date

# Create your views here.
# def search(request):
#     start_str = request.GET.get("start_date")
#     end_str = request.GET.get("end_date")
#     guests = int(request.GET.get("guests", 1))

#     start = parse_date(start_str) if start_str else None
#     end = parse_date(end_str) if end_str else None

#     rooms = (Room.objects
#             .filter(is_active=True, property__is_approved=True, max_guests__gte=guests )
#             .prefetch_related("guest_prices", "price_rules")
#     )

#     if start and end:
#         conflict_bookings = Booking.objects.filter(
#             status__in=["pending_payment", "await_partner_confirm", "confirmed"]

#         ).filter(
#             Q(start_date__lt=end) & Q(end_date__gt=start)
#         ).values_list("room_id", flat=True)

#         conflict_blocks = Room.objects.filter(
#             block_dates__start_date__lt=end,
#             block_dates__end_date__gt=start,
#         ).values_list("id", flat=True)

#         rooms = rooms.exclude(id__in=conflict_bookings).exclude(id__in=conflict_blocks)

#     price_map = {}
#     if start and end:
#         for r in rooms:
#             total = r.calc_total_price(start, end, guests)
#             if total is not None:
#                 price_map[r.id] = total

#     context = {
#         "rooms": rooms,
#         "start_date": start,
#         "end_date": end,
#         "guests": guests,
#         "price_map": price_map
#     }

#     return render(request, "properties/search_results.html", context )

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