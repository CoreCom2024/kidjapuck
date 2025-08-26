from django.utils.timezone import now

def notify_partner_payment_received(booking):
    print(f"[{now()}] [NOTIFY PARTNER] slip uploaded for booking #{booking.id}")

def notify_customer_booking_confirmed(booking):
    print(f"[{now()}] [NOTIFY CUSTOMER] booking #{booking.id} confirmed")