"""
Job-related models.
"""
import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from apps.core.models import TimeStampedModel, SoftDeleteModel, ActiveModel, SortableModel


class Province(TimeStampedModel, ActiveModel, SortableModel):
    """
    Lao provinces (18 ແຂວງ).
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='ຊື່ແຂວງ'
    )
    name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ຊື່ພາສາອັງກິດ'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'ແຂວງ'
        verbose_name_plural = 'ແຂວງ'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_job_count(self):
        return self.job_posts.filter(status='published').count()


class Category(TimeStampedModel, ActiveModel, SortableModel):
    """
    Job categories.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='ຊື່ໝວດໝູ່'
    )
    name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ຊື່ພາສາອັງກິດ'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='ໄອຄອນ'
    )

    class Meta:
        verbose_name = 'ໝວດໝູ່'
        verbose_name_plural = 'ໝວດໝູ່'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def get_job_count(self):
        return self.job_posts.filter(status='published').count()


class JobPost(TimeStampedModel, SoftDeleteModel):
    """
    Job posting model.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'ຮ່າງ'
        PUBLISHED = 'published', 'ເຜີຍແຜ່ແລ້ວ'
        CLOSED = 'closed', 'ປິດແລ້ວ'
        EXPIRED = 'expired', 'ໝົດອາຍຸ'

    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', 'ເຕັມເວລາ'
        PART_TIME = 'part_time', 'ບາງເວລາ'
        CONTRACT = 'contract', 'ສັນຍາຈ້າງ'
        INTERNSHIP = 'internship', 'ຝຶກງານ'
        FREELANCE = 'freelance', 'ຟຣີແລນ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='job_posts',
        verbose_name='ບໍລິສັດ'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='job_posts',
        verbose_name='ໝວດໝູ່'
    )
    province = models.ForeignKey(
        Province,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='job_posts',
        verbose_name='ແຂວງ'
    )

    # Job details
    title = models.CharField(
        max_length=200,
        verbose_name='ຕຳແໜ່ງງານ'
    )
    description = models.TextField(
        verbose_name='ລາຍລະອຽດວຽກ'
    )
    requirements = models.TextField(
        blank=True,
        verbose_name='ຄຸນສົມບັດ'
    )
    benefits = models.TextField(
        blank=True,
        verbose_name='ສະຫວັດດີການ'
    )

    # Salary
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='ເງິນເດືອນຕ່ຳສຸດ'
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='ເງິນເດືອນສູງສຸດ'
    )
    salary_negotiable = models.BooleanField(
        default=False,
        verbose_name='ຕາມຕົກລົງ'
    )

    # Job type
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
        verbose_name='ປະເພດວຽກ'
    )
    positions_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='ຈຳນວນຕຳແໜ່ງ'
    )

    # Contact information
    contact_email = models.EmailField(
        blank=True,
        verbose_name='ອີເມວຕິດຕໍ່'
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='ເບີໂທຕິດຕໍ່'
    )
    contact_whatsapp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='WhatsApp'
    )
    contact_messenger = models.URLField(
        blank=True,
        verbose_name='Messenger'
    )

    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name='ສະຖານະ'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='ວັນທີເຜີຍແຜ່'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='ວັນທີໝົດອາຍຸ'
    )

    # Statistics
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='ຈຳນວນເບິ່ງ'
    )

    # Full-text search (PostgreSQL only)
    # search_vector = SearchVectorField(null=True)

    class Meta:
        verbose_name = 'ໂພສວຽກ'
        verbose_name_plural = 'ໂພສວຽກ'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['province', 'status']),
            # GinIndex(fields=['search_vector']),  # For PostgreSQL
        ]

    def __str__(self):
        return f'{self.title} - {self.company.company_name}'

    def publish(self):
        """Publish the job post."""
        from django.conf import settings

        expiry_days = settings.LAO_JOBS.get('JOB_POST_EXPIRY_DAYS', 15)

        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.expires_at = self.published_at + timedelta(days=expiry_days)
        self.save()

    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def days_remaining(self):
        if not self.expires_at:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

    def get_salary_display(self):
        """Get formatted salary display."""
        from apps.core.utils import format_salary_range
        return format_salary_range(
            int(self.salary_min) if self.salary_min else None,
            int(self.salary_max) if self.salary_max else None,
            self.salary_negotiable
        )


class JobApplication(TimeStampedModel):
    """
    Quick apply job application.
    """

    class Status(models.TextChoices):
        NEW = 'new', 'ໃໝ່'
        VIEWED = 'viewed', 'ເບິ່ງແລ້ວ'
        CONTACTED = 'contacted', 'ຕິດຕໍ່ແລ້ວ'
        REJECTED = 'rejected', 'ປະຕິເສດ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    job_post = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='ໂພສວຽກ'
    )

    # Applicant info
    full_name = models.CharField(
        max_length=100,
        verbose_name='ຊື່ເຕັມ'
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
    email = models.EmailField(
        blank=True,
        verbose_name='ອີເມວ'
    )
    cover_message = models.TextField(
        blank=True,
        verbose_name='ຂໍ້ຄວາມ'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='ສະຖານະ'
    )

    class Meta:
        verbose_name = 'ໃບສະໝັກ'
        verbose_name_plural = 'ໃບສະໝັກ'
        ordering = ['-created_at']
        unique_together = ['job_post', 'phone_normalized']

    def __str__(self):
        return f'{self.full_name} - {self.job_post.title}'


class SavedJob(TimeStampedModel):
    """
    Saved jobs for job seekers (stored in local storage + optional sync).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    job_post = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='saves',
        verbose_name='ໂພສວຽກ'
    )
    session_key = models.CharField(
        max_length=40,
        db_index=True,
        verbose_name='Session Key'
    )

    class Meta:
        verbose_name = 'ວຽກທີ່ບັນທຶກ'
        verbose_name_plural = 'ວຽກທີ່ບັນທຶກ'
        unique_together = ['job_post', 'session_key']


class JobAlert(TimeStampedModel):
    """
    Job alerts for job seekers.
    """

    class Channel(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        SMS = 'sms', 'SMS'

    class Frequency(models.TextChoices):
        INSTANT = 'instant', 'ທັນທີ'
        DAILY = 'daily', 'ປະຈຳວັນ'
        WEEKLY = 'weekly', 'ປະຈຳອາທິດ'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
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

    # Filter criteria
    keywords = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='ຄຳຄົ້ນຫາ'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='ໝວດໝູ່'
    )
    province = models.ForeignKey(
        Province,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='ແຂວງ'
    )
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='ເງິນເດືອນຕ່ຳສຸດ'
    )

    # Notification settings
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.WHATSAPP,
        verbose_name='ຊ່ອງທາງແຈ້ງເຕືອນ'
    )
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.INSTANT,
        verbose_name='ຄວາມຖີ່'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='ເປີດໃຊ້ງານ'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='ຢືນຢັນແລ້ວ'
    )
    last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='ສົ່ງລ່າສຸດ'
    )

    class Meta:
        verbose_name = 'ການແຈ້ງເຕືອນວຽກ'
        verbose_name_plural = 'ການແຈ້ງເຕືອນວຽກ'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone_number} - {self.keywords or "ທຸກວຽກ"}'


class QuickFilter(TimeStampedModel, ActiveModel, SortableModel):
    """
    Predefined quick filters for job search.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=50,
        verbose_name='ຊື່ Filter'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='ໄອຄອນ'
    )
    filter_params = models.JSONField(
        default=dict,
        verbose_name='Parameters'
    )

    class Meta:
        verbose_name = 'Quick Filter'
        verbose_name_plural = 'Quick Filters'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class JobTemplate(TimeStampedModel, ActiveModel, SortableModel):
    """
    Job posting templates for employers.
    """

    class TemplateType(models.TextChoices):
        SYSTEM = 'system', 'ລະບົບ'
        CUSTOM = 'custom', 'ກຳນົດເອງ'

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='ຊື່ Template'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='ໄອຄອນ'
    )
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices,
        default=TemplateType.SYSTEM,
        verbose_name='ປະເພດ'
    )
    company = models.ForeignKey(
        'companies.Company',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='job_templates',
        verbose_name='ບໍລິສັດ'
    )

    # Template fields
    title_template = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='ຕຳແໜ່ງ'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='ໝວດໝູ່'
    )
    job_type = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='ປະເພດວຽກ'
    )
    description_template = models.TextField(
        blank=True,
        verbose_name='ລາຍລະອຽດ'
    )
    requirements_template = models.TextField(
        blank=True,
        verbose_name='ຄຸນສົມບັດ'
    )
    benefits_template = models.TextField(
        blank=True,
        verbose_name='ສະຫວັດດີການ'
    )

    class Meta:
        verbose_name = 'Job Template'
        verbose_name_plural = 'Job Templates'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name
