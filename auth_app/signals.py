from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



User = get_user_model()
@receiver(post_save, sender=User)
def user_post_save_receiver(sender, instance, created, *args, **kwargs):
    print(f"Signal is running! Created: {created}")
    if created:
        print(f'New user created: {instance.username}')
        subject = "Confirm your email"
        from_email = "info@videoflix.com"
        to = instance.email
        text_content = "This is an important message."
        html_content = render_to_string("emails/activate_account.html", {"user": instance, "activation_link": f"http://example.com/activate/{instance.id}/token"})
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
# from django.contrib.auth import get_user_model
# User = get_user_model()
# user = User.objects.create_user(username="Tester", email="test@testmail.com", password="Test123$")