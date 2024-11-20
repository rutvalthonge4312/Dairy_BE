from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError



class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password=None, role=None, first_name='', last_name='', email='', **extra_fields):
        try:
            if not phone_number:
                raise ValueError('Phone Number is required')
            if not email:
                raise ValueError('Email is required')
            email = self.normalize_email(email)
            user = self.model(phone_number=phone_number, role=role, first_name=first_name, last_name=last_name, email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        except Exception as e:
            print(e)

    def create_superuser(self, phone_number, password=None, role=None, first_name='', last_name='', email='', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(phone_number, password, role, first_name, last_name, email, **extra_fields)

class User(AbstractUser):
    phone_number = models.CharField(max_length=10, unique=True)
    role = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    isAccount=models.BooleanField(default=False,null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'role', 'first_name', 'last_name']

    objects = UserManager()
def default_expiry():
    return timezone.now() + timedelta(minutes=10)
class OTP(models.Model):
    otp = models.CharField(max_length=6)
    counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    user_email = models.CharField(default="",max_length=200,null=False)
    expires_at = models.DateTimeField(default=default_expiry)

    def is_expired(self):
        return timezone.now() > self.expires_at
    def clean(self):
        if len(self.otp) != 6:
            raise ValidationError("OTP must be exactly 6 characters long.")

    def save(self, *args, **kwargs):
        self.full_clean()  # calls clean method to run validations
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)