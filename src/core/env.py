from typing import Iterable

from environ import Env as BaseEnv
from environ import ImproperlyConfigured


class Env(BaseEnv):
    def allowed(self, *args, values: Iterable):
        if (value := self.str(*args)) not in values:
            raise ImproperlyConfigured(
                f'Value "{value}" is invalid. Allowed values are in {values}'
            )
        return value
