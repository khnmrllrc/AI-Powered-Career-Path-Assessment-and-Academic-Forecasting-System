#!/usr/bin/env python
import os
import django
import sys
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerpath.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from career.forms import RegisterForm


def main():
    # Test registration form
    token = uuid.uuid4().hex[:8]
    form_data = {
        'student_id': f'TEST_{token}',
        'first_name': 'Signal',
        'middle_name': '',
        'last_name': 'Test',
        'suffix': '',
        'email': f'signal.{token}@example.com',
        'password1': 'TestPass123!@#',
        'password2': 'TestPass123!@#',
    }

    form = RegisterForm(data=form_data)
    if form.is_valid():
        user = form.save()
        print("Registration test PASSED!")
        print(f"  Student ID: {user.student_id}")
        print(f"  Email: {user.email}")
        print(f"  QR Code set during registration: {bool(user.qr_code)}")
        print("\nThe IntegrityError is fixed; QR codes are generated on-demand.")
        user.delete()
    else:
        print("Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")


if __name__ == '__main__':
    main()
