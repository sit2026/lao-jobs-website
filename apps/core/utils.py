"""
Utility functions for Lao Jobs project.
"""
import random
import string
import hashlib
from datetime import datetime
from django.utils import timezone
from django.utils.text import slugify as django_slugify


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP code.
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_reference_code(prefix: str = 'REF') -> str:
    """
    Generate a unique reference code.
    Format: PREFIX-YYYYMMDD-XXXXXXXX
    """
    date_part = timezone.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f'{prefix}-{date_part}-{random_part}'


def generate_invoice_number() -> str:
    """
    Generate a unique invoice number.
    Format: INV-YYYYMM-XXXXXX
    """
    date_part = timezone.now().strftime('%Y%m')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'INV-{date_part}-{random_part}'


def generate_payment_reference() -> str:
    """
    Generate a unique payment reference.
    Format: PAY-YYYYMMDD-XXXXXXXX
    """
    return generate_reference_code('PAY')


def slugify(value: str) -> str:
    """
    Create a slug from a string, handling Lao characters.
    """
    # For Lao text, create a hash-based slug
    if any('\u0e80' <= char <= '\u0eff' for char in value):
        # Contains Lao characters - use hash
        hash_value = hashlib.md5(value.encode()).hexdigest()[:8]
        return f'lao-{hash_value}'

    # For non-Lao text, use Django's slugify
    return django_slugify(value)


def format_lak_currency(amount: int) -> str:
    """
    Format LAK currency with thousand separators.
    Example: 2000000 -> "2,000,000 LAK"
    """
    if amount is None:
        return 'ຕາມຕົກລົງ'
    return f'{amount:,.0f} LAK'


def format_salary_range(min_salary: int, max_salary: int, negotiable: bool = False) -> str:
    """
    Format salary range for display.
    """
    if negotiable:
        return 'ຕາມຕົກລົງ'

    if min_salary and max_salary:
        if min_salary == max_salary:
            return format_lak_currency(min_salary)
        return f'{format_lak_currency(min_salary)} - {format_lak_currency(max_salary)}'

    if min_salary:
        return f'ຕັ້ງແຕ່ {format_lak_currency(min_salary)}'

    if max_salary:
        return f'ເຖິງ {format_lak_currency(max_salary)}'

    return 'ຕາມຕົກລົງ'


def calculate_days_remaining(expires_at: datetime) -> int:
    """
    Calculate days remaining until expiration.
    """
    if not expires_at:
        return 0

    now = timezone.now()
    if expires_at <= now:
        return 0

    delta = expires_at - now
    return delta.days


def time_ago(dt: datetime) -> str:
    """
    Return a human-readable time ago string in Lao.
    """
    if not dt:
        return ''

    now = timezone.now()
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30

    if seconds < 60:
        return 'ຫາກໍ່ນີ້'
    elif minutes < 60:
        return f'{int(minutes)} ນາທີກ່ອນ'
    elif hours < 24:
        return f'{int(hours)} ຊົ່ວໂມງກ່ອນ'
    elif days < 7:
        return f'{int(days)} ມື້ກ່ອນ'
    elif weeks < 4:
        return f'{int(weeks)} ອາທິດກ່ອນ'
    else:
        return f'{int(months)} ເດືອນກ່ອນ'


def mask_email(email: str) -> str:
    """
    Mask email for privacy.
    Example: john.doe@example.com -> j***.d**@example.com
    """
    if not email or '@' not in email:
        return email

    local, domain = email.split('@')

    if len(local) <= 2:
        masked_local = local[0] + '*' * len(local[1:])
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

    return f'{masked_local}@{domain}'


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy.
    Example: 020 5555 1234 -> 020 **** 1234
    """
    if not phone:
        return phone

    # Remove non-digits
    digits = ''.join(filter(str.isdigit, phone))

    if len(digits) < 6:
        return phone

    # Show first 3 and last 4 digits
    return f'{digits[:3]} **** {digits[-4:]}'


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length with ellipsis.
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - 3].rsplit(' ', 1)[0] + '...'
