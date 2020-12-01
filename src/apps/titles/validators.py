from django.core.validators import RegexValidator

year_validator = RegexValidator(regex=r'^(19|20)(\d{2})$')
