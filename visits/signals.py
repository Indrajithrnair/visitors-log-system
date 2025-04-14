from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Visit

# Get domain with a fallback to localhost
def get_domain():
    try:
        return settings.DOMAIN
    except AttributeError:
        return '127.0.0.1:8000'

@receiver(post_save, sender=Visit)
def notify_visit_status_change(sender, instance, created, **kwargs):
    """Send notifications when a visit is created or its status changes"""
    
    domain = get_domain()
    
    # When a new visit request is created, notify the resident
    if created:
        subject = f'New Visit Request: {instance.visitor_name}'
        html_message = render_to_string('notifications/new_visit_request.html', {
            'visit': instance,
            'domain': domain,
        })
        
        # Only send if the resident has an email
        if instance.resident.email:
            try:
                send_mail(
                    subject=subject,
                    message=strip_tags(html_message),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.resident.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
        
        # If visitor provided an email, send confirmation
        if instance.visitor_email:
            try:
                subject = f'Your visit to {instance.resident.get_full_name()} is pending approval'
                html_message = render_to_string('notifications/visitor_confirmation.html', {
                    'visit': instance,
                    'domain': domain,
                })
                
                send_mail(
                    subject=subject,
                    message=strip_tags(html_message),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.visitor_email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email to visitor: {e}")
    
    # When a visit request is approved/rejected, notify the visitor (if email available)
    elif instance.status in ['APPROVED', 'REJECTED'] and instance.visitor_email:
        try:
            if instance.status == 'APPROVED':
                subject = f'Your visit to {instance.resident.get_full_name()} has been approved'
                html_message = render_to_string('notifications/visit_approved.html', {
                    'visit': instance,
                    'domain': domain,
                })
            else:  # REJECTED
                subject = f'Your visit to {instance.resident.get_full_name()} has been rejected'
                html_message = render_to_string('notifications/visit_rejected.html', {
                    'visit': instance,
                    'domain': domain,
                    'rejection_reason': instance.rejection_reason
                })
            
            send_mail(
                subject=subject,
                message=strip_tags(html_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.visitor_email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send status update email: {e}")
            
    # Notify security personnel when a visit is approved
    elif instance.status == 'APPROVED':
        try:
            subject = f'Visit for {instance.visitor_name} has been approved'
            html_message = render_to_string('notifications/visit_approval_security.html', {
                'visit': instance,
                'domain': domain,
            })
            
            send_mail(
                subject=subject,
                message=strip_tags(html_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.requested_by.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send security notification: {e}") 