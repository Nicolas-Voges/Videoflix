from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import create_uidb64_and_token, send_mail


User = get_user_model()
@receiver(post_save, sender=User)
def user_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        uidb64, token = create_uidb64_and_token(instance)
        send_mail(uidb64=uidb64, token=token, instance=instance, content_type='activate_account')