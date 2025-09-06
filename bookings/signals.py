# bookings/signals.py (รุ่นยุบเหลือคู่เดียว)
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Booking
from .notifications import (
    notify_customer_booking_confirmed,
    notify_partner_payment_received,
    notify_customer_booking_cancelled,
    notify_customer_booking_awaiting,
)

@receiver(pre_save, sender=Booking, dispatch_uid="booking_cache_old_state_v1")
def cache_old_state(sender, instance: Booking, **kwargs):
    # เก็บค่าก่อนบันทึกเพื่อเทียบหลังบันทึก
    if instance.pk:
        try:
            old = sender.objects.only("status", "payment_slip", "is_sms_sent", "is_sms_cancelled_sent").get(pk=instance.pk)
            instance._old_status = old.status
            instance._old_has_slip = bool(old.payment_slip)
            instance._old_sms_confirm_sent = getattr(old, "is_sms_sent", False)
            instance._old_sms_cancel_sent = getattr(old, "is_sms_cancelled_sent", False)
        except sender.DoesNotExist:
            instance._old_status = None
            instance._old_has_slip = False
            instance._old_sms_confirm_sent = False
            instance._old_sms_cancel_sent = False
    else:
        instance._old_status = None
        instance._old_has_slip = False
        instance._old_sms_confirm_sent = False
        instance._old_sms_cancel_sent = False

@receiver(post_save, sender=Booking, dispatch_uid="booking_react_after_save_v1")
def react_after_save(sender, instance: Booking, created: bool, **kwargs):
    # 1) เพิ่งมี slip ครั้งแรก -> แจ้ง Partner
    now_has_slip = bool(instance.payment_slip)
    if (not getattr(instance, "_old_has_slip", False)) and now_has_slip:
        notify_partner_payment_received(instance)
        notify_customer_booking_awaiting(instance)

    # ถ้าสถานะไม่เปลี่ยน ไม่ต้องทำอะไรต่อ
    old_status = getattr(instance, "_old_status", None)
    if old_status == instance.status and not created:
        return

    # 2) เปลี่ยนเป็น confirmed ครั้งแรก -> แจ้งลูกค้า (กันซ้ำด้วย flag)
    if instance.status == "confirmed" and not getattr(instance, "_old_sms_confirm_sent", False):
        if not getattr(instance, "is_sms_sent", False):
            notify_customer_booking_confirmed(instance)
            sender.objects.filter(pk=instance.pk).update(is_sms_sent=True)

    # 3) เปลี่ยนเป็น cancelled ครั้งแรก -> แจ้งลูกค้า (กันซ้ำด้วย flag)
    if instance.status == "cancelled" and not getattr(instance, "_old_sms_cancel_sent", False):
        if not getattr(instance, "is_sms_cancelled_sent", False):
            notify_customer_booking_cancelled(instance)
            sender.objects.filter(pk=instance.pk).update(is_sms_cancelled_sent=True)
