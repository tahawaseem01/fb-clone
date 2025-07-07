from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile
from django.contrib.auth import get_user_model
User = get_user_model()


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def suggest_new_user_to_others(sender, instance, created, **kwargs):
#     if created:
#         existing_users = User.objects.exclude(id=instance.id)
#         for user in existing_users:
#             FriendSuggestion.objects.get_or_create(suggested_to=user, suggested_user=instance)
