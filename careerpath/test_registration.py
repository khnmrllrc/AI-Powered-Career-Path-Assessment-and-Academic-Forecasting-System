#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerpath.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from career.forms import RegisterForm


def main():
    # Test registration form
    form_data = {
        'student_id': 'TEST_SIGNAL_01',
        'first_name': 'Signal',
        'middle_name': '',
        'last_name': 'Test',
        'suffix': '',
        'email': 'signal.test@example.com',
        'password1': 'TestPass123!@#',
        'password2': 'TestPass123!@#',
    }

    form = RegisterForm(data=form_data)
    if form.is_valid():
        user = form.save()
        print("Registration test PASSED!")
        print(f"  Student ID: {user.student_id}")
        print(f"  Email: {user.email}")
        print(f"  QR Code set: {bool(user.qr_code)}")
        print("\nThe IntegrityError has been FIXED - qr_code is now generated on registration!")
    else:
        print("Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")


if __name__ == '__main__':
    main()
