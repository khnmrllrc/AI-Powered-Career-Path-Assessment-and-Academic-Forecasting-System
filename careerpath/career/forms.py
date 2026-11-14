from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import StudentUser, AssessmentResponse, CareerPath, AssessmentQuestion, AssessmentLibraryFile
import json

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Student ID',
            'id': 'student_id_login',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password_login',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['username'].help_text = None
        self.fields['password'].label = ''

class RegisterForm(UserCreationForm):
    student_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Student ID'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    middle_name = forms.CharField(
        max_length=50, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Middle Name (optional)'
        })
    )
    suffix = forms.CharField(
        max_length=10, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Suffix (optional)'
        })
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email'
        })
    )

    class Meta:
        model = StudentUser
        fields = [
            'student_id', 'first_name', 'middle_name', 'last_name', 
            'suffix', 'email', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default 'username' field if it exists
        if 'username' in self.fields:
            del self.fields['username']
        # Customize password fields
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    @transaction.atomic
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id:
            user = User.objects.select_for_update().filter(student_id=student_id).first()
            if user:
                raise forms.ValidationError("Student ID already registered.")
            user = User.objects.select_for_update().filter(username=student_id).first()
            if user:
                raise forms.ValidationError("This Student ID is already in use.")
        return student_id


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def save(self, commit=True):
        # Don't call super().save() - manually create the user instead
        # This ensures we have full control over all fields
        
        # Extract cleaned data
        student_id = self.cleaned_data['student_id']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        middle_name = self.cleaned_data.get('middle_name', '')
        suffix = self.cleaned_data.get('suffix', '')
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        
        try:
            # Create the user instance manually (qr_code will be generated on-demand later)
            user = StudentUser(
                student_id=student_id,
                username=student_id,  # Set username = student_id for auth
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                suffix=suffix,
                email=email,
                qr_code=None  # QR code generated on-demand
            )
            
            # Set the password using the set_password method for proper hashing
            user.set_password(password)
            
            if commit:
                user.save()
            
            return user
        except Exception as e:
            # If there's an IntegrityError or other database error, provide clear feedback
            if 'UNIQUE constraint failed' in str(e):
                if 'username' in str(e):
                    raise forms.ValidationError("This Student ID is already registered. Please use a different Student ID.")
                elif 'email' in str(e):
                    raise forms.ValidationError("This email is already registered. Please use a different email.")
                elif 'student_id' in str(e):
                    raise forms.ValidationError("This Student ID is already in use. Please use a different Student ID.")
            # Re-raise if it's not one we handle
            raise


class AssessmentQuestionForm(forms.Form):
    """Dynamic form for assessment questions"""
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        
        options = question.get_normalized_options()
        choices = [(i, opt.get('text', '')) for i, opt in enumerate(options)]
        self.fields['answer'] = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            label=question.question_text,
            required=True
        )


class CareerPathSelectionForm(forms.Form):
    """Form for student to select career path for forecasting"""
    career_path = forms.ModelChoiceField(
        queryset=CareerPath.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Select Career Path',
        required=True
    )


class CounselorNotesForm(forms.Form):
    """Form for counselor to add notes to student report"""
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter notes and observations...'
        }),
        label='Counselor Notes',
        required=False
    )
    is_flagged = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Flag for Follow-up',
        required=False
    )


class AssessmentLibraryFileForm(forms.ModelForm):
    class Meta:
        model = AssessmentLibraryFile
        fields = ['title', 'course_category', 'description', 'file', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assessment file title',
            }),
            'course_category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short note for counselors or students',
            }),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AssessmentTestAdminForm(forms.Form):
    SUBJECT_CHOICES = [
        ('Mathematics', 'Mathematics'),
        ('Science', 'Science'),
        ('English', 'English'),
        ('Filipino', 'Filipino'),
        ('Information Technology', 'Information Technology'),
        ('Social Studies', 'Social Studies'),
        ('Research', 'Research'),
        ('Communication', 'Communication'),
        ('Analytical Skills', 'Analytical Skills'),
        ('Technical Skills', 'Technical Skills'),
    ]

    question_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter the assessment question'
        }),
        label='Question',
    )
    question_type = forms.ChoiceField(
        choices=AssessmentQuestion.QUESTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assessment Type',
    )
    subject = forms.ChoiceField(
        choices=[('', 'Select a subject')] + SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Subject Category',
        required=False,
    )
    custom_subject = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or enter a custom subject'
        }),
        label='Custom Subject',
    )
    order = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to place at the end'
        }),
        label='Display Order',
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Active',
    )

    option_1_text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}), label='Option 1')
    option_1_points = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Mathematics=5, Logic=2'}), label='Option 1 Scoring')
    option_2_text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 2'}), label='Option 2')
    option_2_points = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Mathematics=4'}), label='Option 2 Scoring')
    option_3_text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 3'}), label='Option 3')
    option_3_points = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Mathematics=3'}), label='Option 3 Scoring')
    option_4_text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 4'}), label='Option 4')
    option_4_points = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Mathematics=2'}), label='Option 4 Scoring')
    option_5_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 5 (optional)'}), label='Option 5')
    option_5_points = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Mathematics=1'}), label='Option 5 Scoring')

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)

        if instance:
            normalized_options = instance.get_normalized_options()
            initial = {
                'question_text': instance.question_text,
                'question_type': instance.question_type,
                'order': instance.order,
                'is_active': instance.is_active,
            }

            subject_values = {value for value, _ in self.SUBJECT_CHOICES}
            if instance.category in subject_values:
                initial['subject'] = instance.category
            else:
                initial['custom_subject'] = instance.category

            for index, option in enumerate(normalized_options[:5], start=1):
                initial[f'option_{index}_text'] = option['text']
                initial[f'option_{index}_points'] = self._serialize_points(option['points'])

            self.initial.update(initial)

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject', '').strip()
        custom_subject = cleaned_data.get('custom_subject', '').strip()
        category = custom_subject or subject

        if not category:
            raise forms.ValidationError('Select a subject or enter a custom subject.')

        options = []
        for index in range(1, 6):
            text = (cleaned_data.get(f'option_{index}_text') or '').strip()
            points_raw = (cleaned_data.get(f'option_{index}_points') or '').strip()

            if not text:
                if index <= 4:
                    self.add_error(f'option_{index}_text', 'This option is required.')
                continue

            options.append({
                'text': text,
                'points': self._parse_points(points_raw),
            })

        if len(options) < 4:
            raise forms.ValidationError('Provide at least 4 answer options.')

        cleaned_data['category'] = category
        cleaned_data['options_payload'] = options
        return cleaned_data

    def save(self):
        question = self.instance or AssessmentQuestion()
        question.question_text = self.cleaned_data['question_text']
        question.question_type = self.cleaned_data['question_type']
        question.category = self.cleaned_data['category']
        question.is_active = self.cleaned_data['is_active']
        question.order = self.cleaned_data['order'] or self._get_next_order()
        question.set_options(self.cleaned_data['options_payload'])
        question.save()
        return question

    def _get_next_order(self):
        current_max = AssessmentQuestion.objects.order_by('-order').values_list('order', flat=True).first()
        return (current_max or 0) + 1

    def _parse_points(self, raw_value):
        if not raw_value:
            return {}

        if raw_value.startswith('{'):
            try:
                parsed = json.loads(raw_value)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError as exc:
                raise forms.ValidationError(f'Invalid JSON scoring format: {exc.msg}')

        points = {}
        entries = [entry.strip() for entry in raw_value.split(',') if entry.strip()]
        for entry in entries:
            if '=' not in entry:
                raise forms.ValidationError('Use scoring like Skill=5, Logic=2 or a JSON object.')
            key, value = entry.split('=', 1)
            key = key.strip()
            value = value.strip()
            if not key:
                raise forms.ValidationError('Each scoring entry needs a label before "=".')
            try:
                numeric_value = float(value)
            except ValueError as exc:
                raise forms.ValidationError(f'Invalid score "{value}" for "{key}".') from exc
            points[key] = int(numeric_value) if numeric_value.is_integer() else numeric_value

        return points

    def _serialize_points(self, points):
        if not points:
            return ''
        return ', '.join(f'{key}={value}' for key, value in points.items())
