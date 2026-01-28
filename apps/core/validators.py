"""
Custom validators for Lao Jobs project.
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


# Phone number validator for Laos (+856)
phone_regex = RegexValidator(
    regex=r'^\+?856?\s?0?[0-9]{2}\s?[0-9]{3,4}\s?[0-9]{3,4}$',
    message=_('ເບີໂທບໍ່ຖືກຕ້ອງ. ໃຊ້ຮູບແບບ: 020 1234 5678 ຫຼື +856 20 1234 5678')
)


def normalize_phone_number(phone: str) -> str:
    """
    Normalize Lao phone number to international format.
    Examples:
        020 5555 1234 -> +8562055551234
        +856 20 5555 1234 -> +8562055551234
        0205551234 -> +8562055551234
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Remove leading + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]

    # Remove country code 856 if present
    if cleaned.startswith('856'):
        cleaned = cleaned[3:]

    # Remove leading 0 if present
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]

    # Add country code
    return f'+856{cleaned}'


def validate_lao_phone(value: str) -> None:
    """
    Validate Lao phone number format.
    """
    normalized = normalize_phone_number(value)

    # Check length (should be +856 + 10 digits = 14 chars)
    if len(normalized) < 12 or len(normalized) > 14:
        raise ValidationError(
            _('ເບີໂທບໍ່ຖືກຕ້ອງ. ກະລຸນາໃສ່ເບີໂທ 10 ຫຼັກ.'),
            code='invalid_phone'
        )

    # Check if starts with valid operator prefix
    valid_prefixes = ['20', '30']  # Mobile operators in Laos
    number_part = normalized[4:]  # Remove +856

    if not any(number_part.startswith(prefix) for prefix in valid_prefixes):
        raise ValidationError(
            _('ເບີໂທບໍ່ຖືກຕ້ອງ. ຕ້ອງເລີ່ມຕົ້ນດ້ວຍ 020 ຫຼື 030.'),
            code='invalid_prefix'
        )


def validate_image_size(image):
    """
    Validate image file size (max 2MB).
    """
    max_size = 2 * 1024 * 1024  # 2MB in bytes

    if image.size > max_size:
        raise ValidationError(
            _('ຂະໜາດຮູບພາບໃຫຍ່ເກີນໄປ. ສູງສຸດ 2MB.'),
            code='file_too_large'
        )


def validate_image_extension(image):
    """
    Validate image file extension.
    """
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
    extension = image.name.split('.')[-1].lower()

    if extension not in allowed_extensions:
        raise ValidationError(
            _('ປະເພດໄຟລ໌ບໍ່ຖືກຕ້ອງ. ອະນຸຍາດ: JPG, PNG, WebP'),
            code='invalid_extension'
        )


def validate_salary_range(min_salary, max_salary):
    """
    Validate that min salary is less than max salary.
    """
    if min_salary and max_salary:
        if min_salary > max_salary:
            raise ValidationError(
                _('ເງິນເດືອນຕ່ຳສຸດຕ້ອງໜ້ອຍກວ່າສູງສຸດ.'),
                code='invalid_salary_range'
            )


def validate_no_html(value: str) -> None:
    """
    Validate that the value doesn't contain HTML tags.
    """
    if re.search(r'<[^>]+>', value):
        raise ValidationError(
            _('ບໍ່ອະນຸຍາດໃຫ້ໃຊ້ HTML tags.'),
            code='html_not_allowed'
        )


def validate_no_urls(value: str) -> None:
    """
    Validate that the value doesn't contain URLs.
    """
    url_pattern = r'https?://[^\s]+'
    if re.search(url_pattern, value):
        raise ValidationError(
            _('ບໍ່ອະນຸຍາດໃຫ້ໃສ່ URL.'),
            code='url_not_allowed'
        )
