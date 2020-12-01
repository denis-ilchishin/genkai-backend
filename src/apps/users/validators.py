from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class UnicodeUsernameValidator(RegexValidator):
    regex = r'^[\wа-яА-Я.@+-]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )
