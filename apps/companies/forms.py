"""
Company forms.
"""
from django import forms
from .models import Company
from apps.core.validators import validate_lao_phone, normalize_phone_number


class CompanyProfileForm(forms.ModelForm):
    """
    Form for editing company profile.
    """

    class Meta:
        model = Company
        fields = [
            'company_name',
            'email',
            'phone_number',
            'description',
            'address',
            'province',
            'website',
            'logo',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ຊື່ບໍລິສັດ',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@company.com',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '020 XXXX XXXX',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'ລາຍລະອຽດກ່ຽວກັບບໍລິສັດຂອງທ່ານ...',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 2,
                'placeholder': 'ທີ່ຢູ່ບໍລິສັດ',
            }),
            'province': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://www.example.com',
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/jpeg,image/png,image/webp',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make province choices load lazily
        from apps.jobs.models import Province
        self.fields['province'].queryset = Province.active_objects.all()

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            validate_lao_phone(phone)
            return normalize_phone_number(phone)
        return phone

    def save(self, commit=True):
        company = super().save(commit=False)
        company.phone_normalized = company.phone_number
        if commit:
            company.save()
        return company
