from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives



User = get_user_model()
@receiver(post_save, sender=User)
def user_post_save_receiver(sender, instance, created, *args, **kwargs):
    print(f"Signal is running! Created: {created}")
    if created:
        print(f'New user created: {instance.username}')
        subject = "hello"
        from_email = "from@example.com"
        to = instance.email
        text_content = "This is an important message."
        html_content = "<p>This is an <strong style='color: blue;'>important</strong> message.</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
# from django.contrib.auth import get_user_model
# User = get_user_model()
# user = User.objects.create_user(username="Tester", email="test@testmail.com", password="Test123$")