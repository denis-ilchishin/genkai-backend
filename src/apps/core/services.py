import logging
from pprint import pformat

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

logger = logging.getLogger(__name__)


def google_captcha_verify(captcha: str):
    """Captcha verification method

    Args:
        captcha (str): clients token to verify

    Raises:
        ValidationError: if verification failed
        requests.RequestException: if request is unsuccessful
    """

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


def google_captcha_default_verification(captcha: str):
    """Default api request captcha verification

    Args:
        captcha (str): clients token

    Raises:
        ValidationError: if verify request unsuccessful or captcha verification failed
    """

    try:
        google_captcha_verify(captcha)

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
