from django.utils.timezone import now

def notify_partner_payment_received(booking):
    print(f"[{now()}] [NOTIFY PARTNER] slip uploaded for booking #{booking.id}")

def notify_customer_booking_awaiting(booking):
    print(f"[SMS -> Customer ] Booking #{booking.id} awaiting partner confirm.")

def notify_customer_booking_confirmed(booking):
    print(f"[{now()}] [NOTIFY CUSTOMER] booking #{booking.id} confirmed")

def notify_customer_booking_cancelled(booking):
    phone = getattr(booking.customer, "phone", "N/A")
    print(f"[SMS -> Customer {phone}] Booking #{booking.id} was cancelled."
          f"Deposit refund will be processed. Sorry for the inconvenience.")