import hashlib
import os
import time
from io import BytesIO

from django.core.files import File
from PIL import Image

from storages.backends.s3boto3 import S3Boto3Storage


class ImageStorage(S3Boto3Storage):
    # heights of image variants to save
    sizes = (
        ('small', 100),
        ('medium', 300),
        ('big', 500),
    )

    # image formats and extensions
    formats = (('webp', 'webp'), ('jpeg', 'jpg'))

    # image qualities to save
    qualities = (('2x', 85), ('1x', 70))

    # width to height aspect ratio
    ratio = 1

    # default image format size and quality to serve as storage.url property, format = tuple (format, quality, size)
    default = ('jpeg', '2x', 'big')

    original_suffix = 'original'

    def __init__(self, *args, **kwargs):
        default_format, default_quality, default_size = self.default

        qualities = dict(self.qualities)
        formats = dict(self.formats)
        sizes = dict(self.sizes)

        if default_quality not in qualities:
            raise ValueError(f'{default_quality} not exists in {qualities}')

        if default_size not in sizes:
            raise ValueError(f'{default_size} not exists in {sizes}')

        if default_format not in formats:
            raise ValueError(f'{default_format} not exists in {formats}')

        super().__init__(*args, **kwargs)

    def save(self, name, content):

        # Generate hash for filename
        hashing = hashlib.sha1()
        hashing.update(str(time.time_ns()).encode())
        hashed_name = hashing.hexdigest()

        # Generate new image path to store in db (only path and file's hashed name, without actuall size, quality or extension)
        base_path = os.path.dirname(name)
        hashed_path = os.path.join(base_path, hashed_name)

        # open original
        original_image = Image.open(content)
        original_image.verify()
        original_image = Image.open(content)

        original_name = f'{hashed_path}.{self.original_suffix}'

        # Delete old images
        self.delete_old(name)

        for quality_label, quality in self.qualities:
            for image_format, extension in self.formats:

                new_image = original_image.copy()

                if new_image.mode != 'RGB':
                    # Convert image to rgb mode if it isn't
                    new_image = new_image.convert('RGB')

                for size_label, size in self.sizes:
                    # New image pull path with specific format, size and quality
                    new_image_path = self._generate_file_name(
                        hashed_path, image_format, quality_label, size_label
                    )

                    # Resize image
                    resized_image = self._resized_image(new_image, size, size_label)

                    # Save image
                    self._save_image(
                        new_image_path, resized_image, image_format, quality
                    )
                    resized_image.close()
                new_image.close()

        # Save original image
        self._save(original_name, content)

        original_image.close()

        return hashed_path

    def _save_image(
        self, path: str, image: Image.Image, image_format: str, quality: int
    ):
        io = BytesIO()
        image.save(io, image_format, optimize=True, quality=quality)
        self._save(path, File(io, path))
        io.close()

    @classmethod
    def _resized_image(
        cls, original_image: Image.Image, new_height: int, size_label: str
    ) -> Image.Image:
        orig_width, orig_height = original_image.size

        height = int(new_height)
        width = int(orig_width * height / orig_height)

        # resize image saving the original aspect ratio
        resized_image = original_image.resize((width, height), Image.ANTIALIAS)
        required_width = int(height / cls._get_ratio(size_label))

        # difference between desired width and actual width
        diff_width = width - required_width

        # if actual width is bigger than desired, just crop to fit that width, else crop and resize to fit desired width
        if diff_width >= 0:
            box_width = int((diff_width) / 2)

            box = (
                box_width,
                0,
                required_width + box_width,
                height,
            )
            return resized_image.crop(box)
        else:
            box = (
                0,
                0,
                width,
                height - int(abs(diff_width * cls._get_ratio(size_label))),
            )
            return resized_image.crop(box).resize(
                (required_width, height), Image.ANTIALIAS
            )

    @classmethod
    def _get_ratio(cls, size_label: str) -> int:
        if getattr(cls, 'ratios', None):
            return getattr(cls, 'ratios')[size_label]
        else:
            return cls.ratio

    def _generate_file_name(
        self, base_path: str, image_format: str, quality: str, size: str
    ):
        extension = dict(self.formats).get(image_format)
        return f'{base_path}_{quality}_{size}.{extension}'

    def url(self, filepath: str) -> str:
        return super().url(f'{filepath}.{self.original_suffix}')

    def urls(self, filepath: str) -> dict:

        if not filepath:
            return None

        url_set = {'original': self.url(filepath)}

        for image_format, _ in self.formats:
            if image_format not in url_set:
                url_set[image_format] = {}
            for quality_label, _ in self.qualities:
                if quality_label not in url_set[image_format]:
                    url_set[image_format][quality_label] = {}
                for size_label, _ in self.sizes:
                    url_set[image_format][quality_label][size_label] = super().url(
                        self._generate_file_name(
                            filepath, image_format, quality_label, size_label
                        )
                    )

        return url_set

    def delete_old(self, old):
        """
        Delete old files
        """
        folder = os.path.split(old)[0]
        self.bucket.objects.filter(Prefix=f'{folder}/').delete()
