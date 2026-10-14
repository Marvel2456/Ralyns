import logging
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from .tasks import async_send_email_task

logger = logging.getLogger(__name__)

def dispatch_email(subject, recipient_email, template_name, context, force_sync=False):
    """
    Renders an HTML email template and dispatches it via Celery async worker.
    Falls back to synchronous sending if Celery broker is unavailable.
    """
    context['brand_name'] = "Ralyn's International"
    context['support_email'] = getattr(settings, 'SUPPORT_EMAIL', 'support@ralyns.com')
    context['brand_colors'] = {
        'navy': '#10182C',
        'orange': '#D87808',
        'steel': '#344054',
        'slate': '#64748C',
    }

    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    recipient_list = [recipient_email]

    if not force_sync:
        try:
            async_send_email_task.delay(
                subject=subject,
                recipient_list=recipient_list,
                html_message=html_content,
                text_message=text_content
            )
            logger.info(f"Queued email '{subject}' to {recipient_email} via Celery")
            return True
        except Exception as e:
            logger.warning(f"Celery queueing failed ({e}), falling back to direct send.")

    # Synchronous fallback
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Directly sent email '{subject}' to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {recipient_email}: {e}")
        return False

def send_account_otp_email(user, otp_code):
    """
    Sends the 6-digit verification OTP code on account registration.
    """
    subject = f"Verify Your Ralyn's International Account - OTP: {otp_code}"
    context = {
        'user': user,
        'otp_code': otp_code,
        'customer_code': getattr(user, 'customer_code', 'RAL-NEW'),
    }
    return dispatch_email(subject, user.email, 'emails/account_otp.html', context)

def send_shipment_created_email(shipment):
    """
    Sends booking confirmation and tracking number to customer.
    """
    subject = f"Shipment Confirmed: Tracking #{shipment.tracking_number} - Ralyn's International"
    context = {
        'shipment': shipment,
        'customer': shipment.customer,
        'route': shipment.route,
    }
    return dispatch_email(subject, shipment.customer.email, 'emails/shipment_created.html', context)

def send_shipment_status_update_email(shipment, checkpoint):
    """
    Sends checkpoint/transit status notifications (e.g. In Transit, Customs Cleared, Ready for Delivery).
    """
    subject = f"Update on Shipment #{shipment.tracking_number}: {checkpoint.get_status_display()}"
    context = {
        'shipment': shipment,
        'checkpoint': checkpoint,
        'customer': shipment.customer,
    }
    return dispatch_email(subject, shipment.customer.email, 'emails/shipment_status_update.html', context)

def send_order_confirmation_email(order):
    """
    Sends order receipt and item breakdown for e-commerce purchases.
    """
    subject = f"Order #{order.order_number} Confirmed - Ralyn's International"
    context = {
        'order': order,
        'customer': order.customer,
        'items': order.items.all() if hasattr(order, 'items') else [],
    }
    return dispatch_email(subject, order.customer.email, 'emails/order_confirmation.html', context)
