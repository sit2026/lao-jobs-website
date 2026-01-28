"""
User and authentication models.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('ຕ້ອງໃສ່ອີເມວ')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', User.UserType.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model with email as the unique identifier.
    """

    class UserType(models.TextChoices):
        EMPLOYER = 'employer', 'ນາຍຈ້າງ'
        ADMIN = 'admin', 'ແອດມິນ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        unique=True,
        verbose_name='ອີເມວ'
    )
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.EMPLOYER,
        verbose_name='ປະເພດຜູ້ໃຊ້'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='ໃຊ້ງານຢູ່'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='ເປັນພະນັກງານ'
    )
    is_phone_verified = models.BooleanField(
        default=False,
        verbose_name='ຢືນຢັນເບີໂທແລ້ວ'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP ເຂົ້າສູ່ລະບົບລ່າສຸດ'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'ຜູ້ໃຊ້'
        verbose_name_plural = 'ຜູ້ໃຊ້'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type', 'is_active']),
        ]

    def __str__(self):
        return self.email

    @property
    def is_employer(self):
        return self.user_type == self.UserType.EMPLOYER

    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMIN


class PhoneVerification(TimeStampedModel):
    """
    Model for phone number OTP verification.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'ລໍຖ້າ'
        VERIFIED = 'verified', 'ຢືນຢັນແລ້ວ'
        EXPIRED = 'expired', 'ໝົດອາຍຸ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='phone_verifications',
        verbose_name='ຜູ້ໃຊ້'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='ເບີໂທ'
    )
    phone_normalized = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name='ເບີໂທ (normalized)'
    )
    otp_code = models.CharField(
        max_length=6,
        verbose_name='ລະຫັດ OTP'
    )
    otp_expires_at = models.DateTimeField(
        verbose_name='OTP ໝົດອາຍຸ'
    )
    attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='ຈຳນວນຄັ້ງທີ່ລອງ'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='ສະຖານະ'
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='ເວລາຢືນຢັນ'
    )

    class Meta:
        verbose_name = 'ການຢືນຢັນເບີໂທ'
        verbose_name_plural = 'ການຢືນຢັນເບີໂທ'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone_number} - {self.status}'

    @property
    def is_expired(self):
        return timezone.now() > self.otp_expires_at

    def verify(self, otp_code):
        """
        Verify the OTP code.
        Returns: (success, error_message)
        """
        from django.conf import settings

        max_attempts = settings.LAO_JOBS.get('OTP_MAX_ATTEMPTS', 3)

        # Check if expired
        if self.is_expired:
            self.status = self.Status.EXPIRED
            self.save(update_fields=['status', 'updated_at'])
            return False, 'ລະຫັດ OTP ໝົດອາຍຸ'

        # Check attempts
        if self.attempts >= max_attempts:
            return False, 'ເກີນຈຳນວນຄັ້ງທີ່ອະນຸຍາດ'

        # Increment attempts
        self.attempts += 1
        self.save(update_fields=['attempts', 'updated_at'])

        # Verify code
        if self.otp_code != otp_code:
            return False, 'ລະຫັດ OTP ບໍ່ຖືກຕ້ອງ'

        # Mark as verified
        self.status = self.Status.VERIFIED
        self.verified_at = timezone.now()
        self.save(update_fields=['status', 'verified_at', 'updated_at'])

        # Update user
        self.user.is_phone_verified = True
        self.user.save(update_fields=['is_phone_verified', 'updated_at'])

        return True, None


class LoginAttempt(TimeStampedModel):
    """
    Track login attempts for rate limiting and security.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        verbose_name='ອີເມວ'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP Address'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    success = models.BooleanField(
        default=False,
        verbose_name='ສຳເລັດ'
    )

    class Meta:
        verbose_name = 'ການພະຍາຍາມເຂົ້າສູ່ລະບົບ'
        verbose_name_plural = 'ການພະຍາຍາມເຂົ້າສູ່ລະບົບ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        status = 'ສຳເລັດ' if self.success else 'ລົ້ມເຫຼວ'
        return f'{self.email} - {status}'
