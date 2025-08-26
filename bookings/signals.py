from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Booking
from .notifications import (
    notify_customer_booking_confirmed,
    notify_partner_payment_received,
)

@receiver(pre_save, sender=Booking)
def _cache_before_save(sender, instance: Booking, **kwargs):
    # เก็บค่าก่อนบันทึกไว้ใน instance ก่อนเพื่อเทียบใน post_save
    if not instance.pk:
        instance._old_status = None
        instance._old_has_slip = False
    else:
        try:
            old = Booking.objects.get(pk=instance.pk)
            instance._old_status = old.status
            instance._old_has_slip = bool(old.payment_slip)
        except Booking.DoesNotExist:
            instance._old_status = None
            instance._old_has_slip = False

@receiver(post_save, sender=Booking)
def _react_after_save(sender, instance: Booking, created: bool, **kwargs):
    """
    เหตุการณ์สำคัญ:
    1) อัปโหลดสลิป: จากเดิมไม่มี -> มี => แจ้งพาร์ทเนอร์
    2) เปลี่ยนเป็น confirmed ครั้งแรก => แจ้งลูกค้า (และตั้ง is_sms_sent=True กันซ้ำ)
    """
    #1) slip uploaded
    now_has_slip = bool(instance.payment_slip)
    if (not getattr(instance, "_old_has_slip", False)) and now_has_slip:
        notify_partner_payment_received(instance)

    #2) confired for the first time
    if getattr(instance, "_old_status", None) != "confirmed" and instance.status == "confirmed":
        if not instance.is_sms_sent:
            notify_customer_booking_confirmed(instance)
            Booking.objects.filter(pk=instance.pk).update(is_sms_sent=True)