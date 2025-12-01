import os

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode


def get_content(uidb64, token, instance, content_type):
    """
    Build email subject, plain-text fallback and HTML content.

    The frontend base URL is loaded from settings (FRONTEND_URL).
    It generates the correct activation/reset link depending on content type.
    """
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5500")

    match content_type:
        case 'activate_account':
            subject = "Confirm your email"
            text_content = render_to_string(f"emails/{content_type}.txt", {"user": instance, "activation_link": f"{frontend_url}/pages/auth/activate.html?uid={uidb64}&token={token}"})
            html_content = render_to_string(f"emails/{content_type}.html", {"user": instance, "activation_link": f"{frontend_url}/pages/auth/activate.html?uid={uidb64}&token={token}"})
            return (subject, text_content, html_content)
        case 'reset_password':
            subject = "Reset your password"
            text_content = render_to_string(f"emails/{content_type}.txt", {"user": instance, "reset_link": f"{frontend_url}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"})
            html_content = render_to_string(f"emails/{content_type}.html", {"user": instance, "reset_link": f"{frontend_url}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"})
            return (subject, text_content, html_content)


def create_uidb64_and_token(instance):
    """ Generate a base64-encoded user ID and a secure token for email links. """
    uidb64 = urlsafe_base64_encode(str(instance.pk).encode('utf-8'))
    token = default_token_generator.make_token(instance)
    return (uidb64, token)


def send_mail(uidb64, token, instance, content_type):
    """ Send an email (HTML + text fallback) with activation or password reset content. """
    subject, text_content, html_content = get_content(uidb64, token, instance, content_type)
    from_email = os.getenv("DEFAULT_FROM_EMAIL", "team@videoflix.com")
    to = instance.email
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()