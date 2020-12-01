import logging
from pprint import pformat

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import DjangoValidationError, as_serializer_error, empty
from rest_framework.settings import api_settings

logger = logging.getLogger(__name__)


class CaptchaSerializerMixin(serializers.Serializer):
    captcha = serializers.CharField(required=True, write_only=True)

    def run_validation(self, data=empty):
        """
        We override the default `run_validation`, because the validation
        performed by validators and the `.validate()` method should
        be coerced into an error dictionary with a 'non_fields_error' key.
        """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = self.to_internal_value(data)
        try:
            self.run_validators(value)
            value.pop('captcha')  # remove captcha field from validated data
            value = self.validate(value)
            assert value is not None, '.validate() should return the validated data'
        except (ValidationError, DjangoValidationError) as exc:
            raise ValidationError(detail=as_serializer_error(exc))

        return value

    def validate_captcha(self, value):
        if not settings.DEBUG:
            captcha = value
            try:
                request = requests.post(
                    settings.RECAPTCHA_VERIFY_URL,
                    {'secret': settings.RECAPTCHA_SECRET_KEY, 'response': captcha},
                )

                if request and request.ok:
                    response = request.json()
                    if not response['success']:
                        raise ValidationError()
                else:
                    raise requests.RequestException()

            except ValidationError:
                raise ValidationError(
                    {
                        api_settings.NON_FIELD_ERRORS_KEY: _(
                            'Не удалось верифицировать данный запрос'
                        )
                    }
                )
            except requests.RequestException as e:
                logger.error(
                    'Captcha verification request error.\nRequest token: %s\nResponse: %s',
                    captcha,
                    pformat(e),
                )

                raise ValidationError(
                    {
                        api_settings.NON_FIELD_ERRORS_KEY: _(
                            'Произошла ошибка при верификации запроса. Попробуйте, пожалуйста, позже'
                        )
                    }
                )
