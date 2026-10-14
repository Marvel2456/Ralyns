import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def async_send_email_task(self, subject, recipient_list, html_message, text_message=None):
    """
    Asynchronously sends transactional emails using Django's configured
    email backend (Resend SMTP / Resend API) via Celery and Redis.
    """
    try:
        if not text_message:
            text_message = strip_tags(html_message)
            
        from_email = settings.DEFAULT_FROM_EMAIL
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Successfully queued and sent email '{subject}' to {recipient_list}")
        return True
    except Exception as exc:
        logger.error(f"Error sending email '{subject}' to {recipient_list}: {exc}")
        raise self.retry(exc=exc)
