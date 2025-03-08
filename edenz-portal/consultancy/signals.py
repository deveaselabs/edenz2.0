from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)
    

@receiver(post_save, sender=CustomUser)
def send_approval_email(sender, instance, **kwargs):
    if instance.user_type == 'BUSINESS' and instance.approved:
        try:
            # Check if approval status changed
            if instance.tracker.has_changed('approved') and instance.approved:
                subject = 'Your Business Account Has Been Approved!'
                message = f'''Hello {instance.businessprofile.company_name},
                
Your account with Edenz Consultants has been approved by our administration team.

You can now login to your account:
{settings.SITE_URL}/business/login/

Thank you for choosing Edenz Consultants!

Best regards,
The Edenz Team
'''
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Failed to send approval email: {str(e)}")
