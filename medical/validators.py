import re

from django.core.exceptions import ValidationError


def validate(value, regex, regex_err_msg, is_valid_func=lambda x: True, is_valid_err=None):
    value = value.strip()
    if not re.match(regex, value):
        raise ValidationError(regex_err_msg)
    if not is_valid_func(value):
        raise ValidationError(is_valid_err)


def email_validator(value):
    validate(value,
             regex='^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$',
             regex_err_msg='Your email is not valid.',
             )


def phone_number_validator(value):
    print(value)
    print(str(value).startswith('2547'))
    print(len(value))
    if not str(value).startswith('2547') or not len(value) == 12:
        raise ValidationError('Your phone number must start with 2547 and has 12 digits')