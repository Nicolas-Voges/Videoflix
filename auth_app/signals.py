from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


User = get_user_model()
@receiver(post_save, sender=User)
def user_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        uidb64 = urlsafe_base64_encode(str(instance.pk).encode('utf-8'))
        token = default_token_generator.make_token(instance)
        # user_pk = urlsafe_base64_decode(uidb64).decode('utf_8')
        # print(f"USER_pk: {user_pk}")
        subject = "Confirm your email"
        from_email = "info@videoflix.com"
        to = instance.email
        text_content = "This is an important message."
        html_content = render_to_string("emails/activate_account.html", {"user": instance, "activation_link": f"http://127.0.0.1:8000/api/activate/{uidb64}/{token}/"})
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
# from django.contrib.auth import get_user_model
# User = get_user_model()
# user = User.objects.create_user(username="Tester", email="test@testmail.com", password="Test123$")