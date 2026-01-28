"""
Job forms.
"""
from django import forms
from .models import JobPost, Category, Province
from apps.core.validators import validate_salary_range


class JobPostForm(forms.ModelForm):
    """
    Form for creating/editing job posts.
    """

    class Meta:
        model = JobPost
        fields = [
            'title',
            'category',
            'province',
            'description',
            'requirements',
            'benefits',
            'salary_min',
            'salary_max',
            'salary_negotiable',
            'job_type',
            'positions_count',
            'contact_email',
            'contact_phone',
            'contact_whatsapp',
            'contact_messenger',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ຕຳແໜ່ງວຽກ ເຊັ່ນ: ພະນັກງານບັນຊີ',
            }),
            'category': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'province': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 6,
                'placeholder': 'ອະທິບາຍລາຍລະອຽດວຽກ, ໜ້າທີ່ຮັບຜິດຊອບ...',
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'ຄຸນສົມບັດທີ່ຕ້ອງການ...',
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'ສະຫວັດດີການທີ່ໄດ້ຮັບ...',
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0',
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0',
            }),
            'salary_negotiable': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'positions_count': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'value': '1',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@company.com',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '020 XXXX XXXX',
            }),
            'contact_whatsapp': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+856 20 XXXX XXXX',
            }),
            'contact_messenger': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://m.me/username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.active_objects.all()
        self.fields['province'].queryset = Province.active_objects.all()

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        salary_negotiable = cleaned_data.get('salary_negotiable')

        # Validate salary range
        if not salary_negotiable and salary_min and salary_max:
            if salary_min > salary_max:
                raise forms.ValidationError(
                    'ເງິນເດືອນຕ່ຳສຸດຕ້ອງໜ້ອຍກວ່າສູງສຸດ'
                )

        return cleaned_data


class JobSearchForm(forms.Form):
    """
    Form for job search and filtering.
    """
    q = forms.CharField(
        required=False,
        label='ຄຳຄົ້ນຫາ',
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'ຄົ້ນຫາຕຳແໜ່ງ ຫຼື ບໍລິສັດ...',
        })
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.active_objects.all(),
        label='ໝວດໝູ່',
        empty_label='ທຸກໝວດໝູ່',
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
        })
    )
    province = forms.ModelChoiceField(
        required=False,
        queryset=Province.active_objects.all(),
        label='ແຂວງ',
        empty_label='ທຸກແຂວງ',
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
        })
    )
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'ທຸກປະເພດ')] + list(JobPost.JobType.choices),
        label='ປະເພດວຽກ',
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
        })
    )
    salary_min = forms.DecimalField(
        required=False,
        label='ເງິນເດືອນຕ່ຳສຸດ',
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'ຕ່ຳສຸດ',
        })
    )


class JobApplicationForm(forms.Form):
    """
    Quick apply form.
    """
    full_name = forms.CharField(
        label='ຊື່ເຕັມ',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ທ. ຊື່ ນາມສະກຸນ',
        })
    )
    phone_number = forms.CharField(
        label='ເບີໂທ',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '020 XXXX XXXX',
        })
    )
    email = forms.EmailField(
        required=False,
        label='ອີເມວ (ຖ້າມີ)',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@example.com',
        })
    )
    cover_message = forms.CharField(
        required=False,
        label='ຂໍ້ຄວາມຫາບໍລິສັດ',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'rows': 3,
            'placeholder': 'ແນະນຳຕົວເອງສັ້ນໆ...',
        })
    )

    def clean_phone_number(self):
        from apps.core.validators import validate_lao_phone, normalize_phone_number
        phone = self.cleaned_data.get('phone_number')
        validate_lao_phone(phone)
        return normalize_phone_number(phone)


class JobAlertForm(forms.Form):
    """
    Job alert subscription form.
    """
    phone_number = forms.CharField(
        label='ເບີໂທ',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '020 XXXX XXXX',
        })
    )
    keywords = forms.CharField(
        required=False,
        label='ຄຳຄົ້ນຫາ (ຖ້າມີ)',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ເຊັ່ນ: ບັນຊີ, IT, ຂາຍ',
        })
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.active_objects.all(),
        label='ໝວດໝູ່',
        empty_label='ທຸກໝວດໝູ່',
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
        })
    )
    province = forms.ModelChoiceField(
        required=False,
        queryset=Province.active_objects.all(),
        label='ແຂວງ',
        empty_label='ທຸກແຂວງ',
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
        })
    )

    def clean_phone_number(self):
        from apps.core.validators import validate_lao_phone, normalize_phone_number
        phone = self.cleaned_data.get('phone_number')
        validate_lao_phone(phone)
        return normalize_phone_number(phone)
