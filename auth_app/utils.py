from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode


def get_content(uidb64, token, instance, content_type):
    html_content = render_to_string(f"emails/{content_type}.html", {"user": instance, "activation_link": f"http://127.0.0.1:8000/api/activate/{uidb64}/{token}/"})
    match content_type:
        case 'activate_account':
            subject = "Confirm your email"
            text_content = "This is an important message."
            return (subject, text_content, html_content)
        case 'reset_password':
            subject = "Reset your password"
            text_content = "This is an important message."
            return (subject, text_content, html_content)


def create_uidb64_and_token(instance):
    uidb64 = urlsafe_base64_encode(str(instance.pk).encode('utf-8'))
    token = default_token_generator.make_token(instance)
    return (uidb64, token)


def send_mail(uidb64, token, instance, content_type):
    subject, text_content, html_content = get_content(uidb64, token, instance, content_type)
    from_email = "info@videoflix.com"
    to = instance.email
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()