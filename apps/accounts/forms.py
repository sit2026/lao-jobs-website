"""
Account forms for authentication and registration.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import User


class LoginForm(forms.Form):
    """
    Login form with email and password.
    """
    email = forms.EmailField(
        label='ອີເມວ',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'ໃສ່ອີເມວຂອງທ່ານ',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='ລະຫັດຜ່ານ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'ໃສ່ລະຫັດຜ່ານ',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='ຈຳຂ້ອຍໄວ້',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    'ອີເມວ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ',
                    code='invalid_login'
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    'ບັນຊີນີ້ຖືກລະງັບ',
                    code='inactive'
                )

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class EmployerRegistrationForm(forms.ModelForm):
    """
    Registration form for employers.
    """
    password1 = forms.CharField(
        label='ລະຫັດຜ່ານ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'ຢ່າງໜ້ອຍ 8 ຕົວອັກສອນ',
        })
    )
    password2 = forms.CharField(
        label='ຢືນຢັນລະຫັດຜ່ານ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'ໃສ່ລະຫັດຜ່ານອີກຄັ້ງ',
        })
    )
    company_name = forms.CharField(
        label='ຊື່ບໍລິສັດ',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ຊື່ບໍລິສັດຂອງທ່ານ',
        })
    )
    phone_number = forms.CharField(
        label='ເບີໂທຕິດຕໍ່',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '020 XXXX XXXX',
        })
    )
    agree_terms = forms.BooleanField(
        label='ຂ້ອຍຍອມຮັບເງື່ອນໄຂການໃຊ້ງານ',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@company.com',
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('ອີເມວນີ້ຖືກໃຊ້ແລ້ວ')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('ລະຫັດຜ່ານບໍ່ກົງກັນ')

        if password1 and len(password1) < 8:
            raise forms.ValidationError('ລະຫັດຜ່ານຕ້ອງມີຢ່າງໜ້ອຍ 8 ຕົວອັກສອນ')

        return password2

    def clean_phone_number(self):
        from apps.core.validators import validate_lao_phone, normalize_phone_number

        phone = self.cleaned_data.get('phone_number')
        validate_lao_phone(phone)
        return normalize_phone_number(phone)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.user_type = User.UserType.EMPLOYER

        if commit:
            user.save()

        return user


class OTPVerificationForm(forms.Form):
    """
    Form for OTP verification.
    """
    otp_code = forms.CharField(
        label='ລະຫັດ OTP',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input text-center text-2xl tracking-widest',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric',
            'autofocus': True,
        })
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code')
        if not code.isdigit():
            raise forms.ValidationError('ລະຫັດ OTP ຕ້ອງເປັນຕົວເລກເທົ່ານັ້ນ')
        return code


class ChangePasswordForm(forms.Form):
    """
    Form for changing password.
    """
    current_password = forms.CharField(
        label='ລະຫັດຜ່ານປັດຈຸບັນ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
        })
    )
    new_password1 = forms.CharField(
        label='ລະຫັດຜ່ານໃໝ່',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
        })
    )
    new_password2 = forms.CharField(
        label='ຢືນຢັນລະຫັດຜ່ານໃໝ່',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise forms.ValidationError('ລະຫັດຜ່ານປັດຈຸບັນບໍ່ຖືກຕ້ອງ')
        return current

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('ລະຫັດຜ່ານໃໝ່ບໍ່ກົງກັນ')

        if password1 and len(password1) < 8:
            raise forms.ValidationError('ລະຫັດຜ່ານຕ້ອງມີຢ່າງໜ້ອຍ 8 ຕົວອັກສອນ')

        return password2

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user
