from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import ImageFieldFile

from .validators import image_validator, slug_validator


class BaseImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        image_validator(content)
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(name, content)

        setattr(self.instance, self.field.name, self.name)
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()

    save.alters_data = True

    @property
    def url(self):
        self._require_file()
        return self.storage.url(self.name)

    @property
    def urls(self):
        self._require_file()
        return self.storage.urls(self.name)

    def _require_file(self):
        """Allow value being empty"""
        pass


class BaseImageField(models.ImageField):
    attr_class = BaseImageFieldFile

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)


class SlugField(models.SlugField):
    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python() and validate() are propagated. Return the correct
        value if no error is raised.
        """
        value = self.to_python(value)
        self.validate(value, model_instance)
        self.run_validators(value, model_instance)
        return value

    def run_validators(self, value, model_instance):
        if value in self.empty_values:
            return

        errors = []
        for v in self.validators:
            try:
                if v == slug_validator:
                    v(value, self.model, model_instance)
                else:
                    v(value)
            except ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)

        if errors:
            raise ValidationError(errors)
