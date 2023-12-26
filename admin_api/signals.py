import smtplib
from email.mime.text import MIMEText
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import signals
from accounts.models import CustomUser




@receiver(post_save, sender=CustomUser)
def send_promotional_email(sender, instance, created, **kwargs):
    """
       Admin can send promotional emails to all users
    """
    if not created:
        sender_email = "manager@gmail.com"
        recipient_email = instance.email
        subject = "Offer !!!!"
        context = {'username': instance.username}
 
        # Load the HTML template
        html_message = render_to_string('promo_email.html', context)
 
        # Create a plain text version of the HTML email
        plain_message = strip_tags(html_message)
 
        send_mail(subject, plain_message, sender_email, [recipient_email], html_message=html_message)