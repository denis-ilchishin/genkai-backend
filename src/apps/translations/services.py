import logging
import tempfile
from logging import Logger
from typing import Tuple, Union

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.utils import translation
from django.utils.text import slugify
from requests import Response
from requests.exceptions import RequestException
from transliterate import translit

from apps.content.models import Country, Genre, Studio
from apps.titles.models import Title
from apps.translations.models import Episode, Resolver, Translation, Translator, Update

User = get_user_model()

logger = logging.getLogger(__name__)


class InvalidUpdateItem(Exception):
    pass


class UpdateService:
    def __init__(self, is_testing=False):
        self.is_testing = is_testing

    def _get_url(self) -> str:
        raise NotImplementedError

    def _get_token(self) -> str:
        raise NotImplementedError

    def _get_service(self) -> str:
        raise NotImplementedError

    def _get_params(self) -> dict:
        raise NotImplementedError

    def _get_logger_kwargs(self) -> dict:
        return {'extra': {'service': self.__class__.__name__}}

    def _check_item(self) -> None:
        """Perform validation of update item

        Raises:
            InvalidUpdateItem: If update item is not valid
        """
        raise NotImplementedError

    def _parse_item(self) -> list:
        """Parse update item

        Raises:
            InvalidUpdateItem: If update item is not valid

        Returns:
            list: List of added episodes
        """
        raise NotImplementedError

    def _request(self, url: str = '', params: dict = {}) -> Response:
        try:
            params = self._get_params() if not url else params
            url = url or self._get_url()

            response: Response = requests.post(url, params, timeout=10)
            if response.ok:
                logger.info(
                    '%(url)s - Request successfull with params %(params)s',
                    {'url': url, 'params': params},
                    **self._get_logger_kwargs(),
                )
                return response
            else:
                logger.error(
                    '%(status)s status code %(url)s, response %(response)s - Request failed with params %(params)s',
                    {
                        'status': response.status_code,
                        'url': url,
                        'response': response.text,
                        'params': params,
                    },
                    **self._get_logger_kwargs(),
                )

        except RequestException:
            logger.exception(
                '%(url)s - Request failed with params %(params)s',
                {'url': url, 'params': params},
                **self._get_logger_kwargs(),
            )

    def _update(self) -> Tuple[list, bool]:
        raise NotImplementedError

    def update(self) -> None:
        logger.info('BEGIN', **self._get_logger_kwargs())
        update = Update()
        added_episodes, with_errors = self._update()
        if self.is_testing:
            print(
                'Added episodes: %(episodes)s. With errors: %(with_errors)s'
                % {
                    'episodes': len(added_episodes),
                    'with_errors': 'Yes' if with_errors else 'No',
                }
            )
        update.without_errors = not with_errors
        update.save()
        update.added_episodes.add(*added_episodes)
        logger.info('FINISH\n\n', **self._get_logger_kwargs())


class KodikUpdateService(UpdateService):
    kodik_types = {
        'tv': Title.TYPES.series,
        'movie': Title.TYPES.movie,
        'ova': Title.TYPES.ova,
        'ona': Title.TYPES.ona,
        'special': Title.TYPES.special,
        'tv_13': Title.TYPES.series,
        'tv_24': Title.TYPES.series,
        'tv484': Title.TYPES.series,
    }

    kodik_statuses = {
        'anons': Title.STATUSES.announce,
        'ongoing': Title.STATUSES.ongoing,
        'released': Title.STATUSES.released,
    }

    kodik_age_ratings = {
        'G': Title.AGE_RATINGS.g,
        'PG': Title.AGE_RATINGS.pg,
        'PG-13': Title.AGE_RATINGS.pg_13,
        'R': Title.AGE_RATINGS.r,
        'R+': Title.AGE_RATINGS.nc_17,
        'Rx': Title.AGE_RATINGS.nc_17,
    }

    def _get_fields_to_check(self) -> list:
        raise NotImplementedError

    def _check_item(self, item):
        for field in self._get_fields_to_check():
            if field not in item:
                raise InvalidUpdateItem(f'Field [{field}] is missing')

    def _get_service(self) -> str:
        return settings.SERVICES.kodik

    def _get_token(self) -> str:
        return settings.KODIK_API_TOKEN

    def _get_url(self) -> str:
        return settings.KODIK_API_URL

    def _get_types(self) -> list:
        raise NotImplementedError

    def _get_params(self) -> dict:
        return {
            'token': self._get_token(),
            'types': self._get_types(),
            'sort': 'updated_at',
            'with_seasons': 1,
            'with_episodes': 1,
            'with_material_data': 1,
            'limit': 100 if not self.is_testing else 10,
        }

    def _set_material_data(self, data: dict, title: Title) -> None:
        if 'material_data' in data:
            try:
                title.description = data['material_data']['description'].strip()
            except KeyError:
                pass

            try:
                if other_name := data['material_data']['title'].strip():
                    title.other_names.append(other_name)
            except KeyError:
                pass

            try:
                if other_name := data['material_data']['title_en'].strip():
                    title.other_names.append(other_name)
            except KeyError:
                pass

            try:
                for country_name in data['material_data']['countries']:
                    country, is_new = Country.objects.get_or_create(
                        defaults={
                            'name': country_name.strip(),
                            'slug': slugify(
                                translit(country_name.strip(), 'ru', reversed=True),
                                allow_unicode=True,
                            ),
                        },
                        name__iexact=country_name.strip(),
                    )
                    title.countries.add(country)
            except KeyError:
                pass

            try:
                for genre_name in data['material_data']['anime_genres']:
                    genre, is_new = Genre.objects.get_or_create(
                        defaults={
                            'name': genre_name.strip(),
                            'slug': slugify(
                                translit(genre_name.strip(), 'ru', reversed=True),
                                allow_unicode=True,
                            ),
                        },
                        name__iexact=genre_name.strip(),
                    )
                    title.genres.add(genre)
            except KeyError:
                pass

            try:
                for studio_name in data['material_data']['anime_studios']:
                    studio, is_new = Studio.objects.get_or_create(
                        defaults={
                            'name': studio_name.strip(),
                            'slug': slugify(
                                translit(studio_name.strip(), 'ru', reversed=True),
                                allow_unicode=True,
                            ),
                        },
                        name__iexact=studio_name.strip(),
                    )
                    title.studios.add(studio)
            except KeyError:
                pass

            try:
                title.duration = data['material_data']['duration']
            except KeyError:
                pass

            try:
                title.total_episodes = data['material_data']['episodes_total']
            except KeyError:
                pass

            try:
                title.age_rating = self.kodik_age_ratings[
                    data['material_data']['rating_mpaa']
                ]
            except KeyError:
                pass

            try:
                title.status = self.kodik_statuses[
                    data['material_data']['anime_status']
                ]
            except KeyError:
                pass

            try:
                title.type = self.kodik_types[data['material_data']['anime_kind']]
            except KeyError:
                pass

            title.save()

    def _get_translation(
        self, id: Union[str, int], season: Union[str, int], url: str
    ) -> Tuple[Translation, bool]:
        try:
            return Translation.objects.get_or_create(
                defaults={'url': url,},
                external_id=id,
                service=self._get_service(),
                title__season=season,
            )
        except Translation.MultipleObjectsReturned:
            raise InvalidUpdateItem(
                f"Fount multiple translations with: title__season=[{season}] | external_id=[{id}] | service={self._get_service()}"
            )

    def _get_translator(self, data, translation: Translation) -> Translator:
        if translation.translator:
            return translation.translator
        else:

            try:
                resolver, is_new = Resolver.objects.get_or_create(
                    model=Resolver.MODELS.translator,
                    external_id=data['translation']['id'],
                    service=self._get_service(),
                )
            except MultipleObjectsReturned:
                # Normally, shouldn't happen
                raise InvalidUpdateItem(
                    f"Fount multiple resolvers with: model={Resolver.MODELS.translator} | external_id={data['translation']['id']} | service={self._get_service()}"
                )

            translator = None
            if resolver.internal_id:
                translator = Translator.objects.get_or_none(pk=resolver.internal_id)

            if translator is None:
                translator = Translator.objects.create(
                    name=data['translation']['title'].strip()
                )

            if resolver.internal_id != translator.pk:
                resolver.internal_id = translator.pk
                resolver.save()

            translation.translator = translator

            return translator

    def _get_title(
        self, data: dict, season: Union[str, int], translation: Translation
    ) -> Tuple[Title, bool]:

        if translation.title:
            return translation.title, False
        else:
            other_names = []

            try:
                for name in data['title_orig'].split('/'):
                    if (name := name.strip()) not in other_names:
                        other_names.append(name)
            except KeyError:
                pass

            try:
                for name in data['other_title'].split('/'):
                    if (name := name.strip()) not in other_names:
                        other_names.append(name)
            except KeyError:
                pass

            try:
                try:
                    title, is_new = Title.objects.get_or_create(
                        shikimori_id=data['shikimori_id'],
                        season=season,
                        defaults={
                            'name': data['title'].strip(),
                            'shikimori_id': data['shikimori_id'],
                            'other_names': other_names,
                            'year': data['year'] if 'year' in data else 0,
                        },
                    )
                except KeyError:
                    title, is_new = Title.objects.get_or_create(
                        season=season,
                        name__iexact=data['title'].strip(),
                        defaults={
                            'name': data['title'].strip(),
                            'other_names': other_names,
                            'year': data['year'] if 'year' in data else 0,
                        },
                    )
            except MultipleObjectsReturned:
                # Normally shouldn't happen
                raise InvalidUpdateItem(
                    f"Found multiple titles with: name={data['title'].strip()} | type={type} | season={season}"
                )

            translation.title = title

            return title, is_new

    def _set_episodes(self, episodes, translation: Translation) -> list:
        new_episodes = []
        for number, link in episodes.items():
            try:
                number = int(number.strip())
            except ValueError:
                logger.info('Some weird episode number: %(number)s', {'number', number})
                continue

            episode, is_new = Episode.objects.get_or_create(
                defaults={'url': link,}, number=number, translation=translation,
            )

            if is_new:
                new_episodes.append(episode)
        return new_episodes


class SeriesKodikUpdateService(KodikUpdateService):
    def _get_fields_to_check(self) -> list:
        return ['id', 'type', 'title', 'seasons', 'translation']

    def _get_types(self) -> list:
        return ['anime-serial']

    def _parse_item(self, item) -> list:
        self._check_item(item)
        added_episodes = []
        for season, season_data in item['seasons'].items():

            translation, is_new_translation = self._get_translation(
                item['id'], season, season_data['link']
            )
            title, is_new_title = self._get_title(item, season, translation)

            translator = self._get_translator(item, translation)

            translation.save()

            if is_new_title:
                self._set_material_data(item, title)

            added_episodes.extend(
                self._set_episodes(item['seasons'][season]['episodes'], translation)
            )
        return added_episodes

    def _update(self) -> Tuple[list, bool]:
        new_episodes = []
        with_errors = False
        try:
            response = self._request()
            while response:
                data = response.json()
                results = data['results']

                for item in results:
                    try:
                        added_episodes = self._parse_item(item)
                        new_episodes.extend(added_episodes)

                    except InvalidUpdateItem as ex:
                        if self.is_testing:
                            print(ex)

                        with_errors = True
                        logger.exception(
                            'Error during parsing item: %(item)s',
                            {'item': item},
                            **self._get_logger_kwargs(),
                        )

                if self.is_testing:
                    # stop fetching next pages if is running tests
                    break

                if 'next_page' in data and data['next_page']:
                    response = self._request(data['next_page'])
                else:
                    break

        except Exception as ex:
            if self.is_testing:
                print(ex)

            with_errors = True
            logger.exception(
                'Error during perfoming update', **self._get_logger_kwargs()
            )
        return new_episodes, with_errors


class MoviesKodikUpdateService(KodikUpdateService):
    def _get_fields_to_check(self) -> list:
        return ['id', 'link', 'type', 'title', 'translation']

    def _get_types(self) -> list:
        return ['anime']

    def _parse_item(self, item) -> list:
        self._check_item(item)

        translation, is_new_translation = self._get_translation(
            item['id'], None, item['link']
        )
        title, is_new_title = self._get_title(item, None, translation)
        translator = self._get_translator(item, translation)

        translation.save()

        if is_new_title:
            self._set_material_data(item, title)

        episode, is_new_episode = Episode.objects.get_or_create(
            defaults={'url': item['link'],}, number=1, translation=translation,
        )

        return [episode] if is_new_episode else []

    def _update(self) -> Tuple[list, bool]:
        new_episodes = []
        with_errors = False
        response = self._request()
        try:
            while response:
                data = response.json()
                results = data['results']

                for item in results:
                    try:
                        added_episodes = self._parse_item(item)
                        new_episodes.extend(added_episodes)
                        if self.is_testing:
                            logger.info(
                                'Added episodes: %s',
                                len(added_episodes),
                                **self._get_logger_kwargs(),
                            )
                    except InvalidUpdateItem:
                        with_errors = True
                        logger.exception(
                            'Error during parsing item: %(item)s',
                            {'item': item},
                            **self._get_logger_kwargs(),
                        )

                if self.is_testing:
                    break

                if 'next_page' in data and data['next_page']:
                    response = self._request(data['next_page'])
                else:
                    break

        except Exception:
            with_errors = True
            logger.exception(
                'Error during perfoming update', **self._get_logger_kwargs()
            )
        return new_episodes, with_errors
