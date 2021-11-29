from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy
from project.models import Project, Role
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set !")

        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE = (
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Member', 'Member'),
        ('Contact', 'Contact'),
    )
    user_type  = models.CharField(max_length=10, choices=USER_TYPE, default='Admin')
    username   = models.CharField(max_length=50, blank=True, null=True)
    email      = models.EmailField(unique=True, null=False)
    co_manager = models.BooleanField(default=False)
    is_staff   = models.BooleanField(
        ugettext_lazy("Staff Status"),
        default=False,
        help_text="Designates whether user can login this site !"
    )
    is_active = models.BooleanField(
        ugettext_lazy("Active"),
        default=True,
        help_text="Designates whether user treated as an active user ! Unselect this in stated of deleting "
                  "account !"
    )
    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.username:
            return f"{self.username} ( {self.user_type} )"
        return f"{self.email} ( {self.user_type} )"

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


def upload_profile_image(instance, filename):
    return '/'.join(['profile_image', str(instance.user.username), filename])


class Profile(models.Model):
    GENDER = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Others", "Others"),
    )
    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_no          = models.CharField(max_length=100, blank=True, null=True)
    portfolio_link    = models.URLField(null=True, blank=True)
    profile_image     = models.FileField(upload_to=upload_profile_image, null=True, blank=True)
    gender            = models.CharField(max_length=10, choices=GENDER, default="Male")
    invited_by        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles', blank=True, null=True)
    projects          = models.ManyToManyField(Project, blank=True) # This field should be related with Project table
    roles             = models.ManyToManyField(Role, blank=True) # This field should be related with Role table
    timestamp         = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username}' profile"

    class Meta:
        ordering = ['-timestamp', ]




@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()