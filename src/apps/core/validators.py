from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image

not_supported_or_invalid = _('Данный тип не поддерживается или файл поврежден')


def slug_validator(value, model, instance):
    if model.objects.filter(slug=value).exclude(pk=instance.pk).exists():
        raise ValidationError(_('Slug is not unique'))


def image_validator(value):

    try:
        image: Image.Image = Image.open(value)
        image.verify()
    except Exception:
        raise ValidationError(not_supported_or_invalid)
