import datetime
import json
import logging
import pprint
from urllib.parse import urlparse

import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pywebpush import WebPushException, webpush
from requests.exceptions import ConnectionError

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer

logger = logging.getLogger(__name__)


def _get_jwt_token(endpoint: str) -> str:
    return jwt.encode(
        {
            'aud': '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(endpoint)),
            'exp': int(datetime.datetime.now().timestamp()) + 3600,
            'sub': settings.FRONTEND_URL,
        },
        key=settings.PUSH_NOTIFICATIONS_PRIVATE_KEY.encode(),
        algorithm='ES256',
    ).decode()


def _send_webpush(token: str, subscription_object: dict, notification: Notification):
    return webpush(
        subscription_object,
        data=json.dumps(
            {
                'title': str(_('Genkai - смотреть аниме онлайн')),
                'text': notification.get_push_notification_text(),
                'url': notification.get_push_notification_url(),
                'notification': NotificationSerializer(notification).data,
                'notifications_count': notification.user.get_not_seen_notifications_count(),
            }
        ),
        vapid_private_key=settings.PUSH_NOTIFICATIONS_PRIVATE_KEY,
        headers={
            'Authorization': f'WebPush {token}',
            'Crypto-Key': f'p256ecdsa={settings.PUSH_NOTIFICATIONS_BASE64_PUBLIC_KEY}',
        },
    )


def send_push_notification(notification: Notification):
    """Send push notification to `notification` user's push notification subscriptions.

    Args:
        notification (Notification): Notification model instance
    """
    if notification and notification.user.push_notification_subscriptions.count():
        for (
            push_notification_subscription
        ) in notification.user.push_notification_subscriptions.all():
            subscription_object = push_notification_subscription.subscription
            token = _get_jwt_token(endpoint=subscription_object['endpoint'])
            try:
                logger.info(
                    'Sending push notification ID [%s] to push notification subscription ID [%s]',
                    notification.id,
                    push_notification_subscription.id,
                )
                response = _send_webpush(token, subscription_object, notification)
                logger.info(
                    'Result of push notification ID [%s] to push notification subscription ID [%s]: \n%s',
                    notification.id,
                    push_notification_subscription.id,
                    pprint.pformat(response),
                )
            except WebPushException as exception:
                if (
                    exception.response is not None
                    and int(exception.response.status_code) == 410
                ):
                    logger.info(
                        'Deteled user ID [%s]\'s push notification subscription because it has been unsubscribed or invalid',
                        notification.user.id,
                    )
                    push_notification_subscription.delete()
                else:
                    logger.exception(
                        'Unexpected error for - user ID [%s] | push notification subscription ID [%s] : \n%s',
                        notification.user.id,
                        push_notification_subscription.id,
                        pprint.pformat(push_notification_subscription.subscription),
                    )
            except ConnectionError as exception:
                logger.exception(
                    'Failed to establish a new connection - user ID [%s] | push notification subscription ID [%s] : \n%s',
                    notification.user.id,
                    push_notification_subscription.id,
                    pprint.pformat(push_notification_subscription.subscription),
                )
