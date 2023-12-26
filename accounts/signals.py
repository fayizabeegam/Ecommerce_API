import smtplib
from email.mime.text import MIMEText
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import *
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import signals
from .models import Order
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
 
@receiver(post_save, sender=User)
def send_registration_email(sender, instance, created, **kwargs):
    """
       sending a registeration notification
    """
    if created:  
        sender_email = "admin@gmail.com" 
        recipient_email = instance.email
        subject = "Welcome To Ecommerce Home !!"
        body = f"Hello {instance.username},\n\nThank you for registering !"
 
        msg = MIMEText(body)
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
 
        smtp_server = 'smtp.mailtrap.io'
        smtp_port = 2525
        smtp_username = '2607a1e4f9cc84'
        smtp_password = 'c25153aff8e14d'
 
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
 
 
 
@receiver(post_save, sender=CustomUser)
def send_registration_email_custom_user(sender, instance, created, **kwargs):
    if created: 
        sender_email = "admin@gmail.com"  
        recipient_email = instance.email
        subject = "Welcome To Ecommerce Home!!"
        body = f"Hello {instance.username},\n\nThank you for registering !"
 
        msg = MIMEText(body)
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
 
        smtp_server = 'smtp.mailtrap.io'
        smtp_port = 2525
        smtp_username = '2607a1e4f9cc84'
        smtp_password = 'c25153aff8e14d'
 
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()



@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    """
      sending an order confirmation mail to user
    """
    if created:
        # Send email to the user
        user_subject = "Your Order Placed Successfully"
        user_message = render_to_string('order_update_user.html', {'order': instance})
        user_email = instance.user.email
        send_mail(user_subject, strip_tags(user_message), 'manager@gmail.com', 
                  [user_email], html_message=user_message)
 
        # Send email to the admin
        admin_subject = "New Order Placed"
        admin_message = render_to_string('order_update_admin.html', {'order': instance})
        admin_email = 'admin@gmail.com'  # Replace with the admin's email address
        send_mail(admin_subject, strip_tags(admin_message), 'manager@gmail.com',
                   [admin_email], html_message=admin_message)
 
 

@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, **kwargs):
    """
       sending an order status to user
    """

    if kwargs.get('update_fields') is None or 'status' in kwargs['update_fields']:
        # Check if the 'status' field is updated
 
        # Send email to the user
        user_subject = " Your Order Status "
        user_message = render_to_string('order_update_status.html', {'order': instance})
        user_email = instance.user.email
        send_mail(user_subject, strip_tags(user_message), 'manager@gmail.com', 
                  [user_email], html_message=user_message)




@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    """
       password reset mail for user
    """
    
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/password_reset_email.html', context)
    email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Ecommerce"),
        # message:
        email_plaintext_message,
        # from:
        "manager@domain.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()