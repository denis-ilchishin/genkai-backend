import hashlib

from apps.core.storages import ImageStorage


def user_image_path(user, filename):
    if not user.pk:
        return 'temp/{}'.format(filename)
    else:
        hashing = hashlib.sha1()
        hashing.update(str(user.pk).encode())
        return 'user/{}/{}'.format(hashing.hexdigest(), filename)


class UserImageStorage(ImageStorage):
    pass
