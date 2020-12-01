from django.conf import settings
from django.views.generic import TemplateView

from apps.titles.models import Title
from apps.titles.views import CurrentSeason, Latests, Populars
from apps.translations.models import Episode
from apps.translations.views import Updates
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response

from .services import get_frontend_app_config


class FrontendConfig(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response(get_frontend_app_config())


class FrontendHome(APIView):
    def get_list_view_data(self, view: GenericAPIView, limit: int = None):
        view = view(request=self.request)

        queryset = view.get_queryset()

        if limit:
            queryset = queryset[:limit]

        serializer = view.serializer_class(
            queryset, many=True, context={'request': self.request}
        )

        return serializer.data

    def get(self, request):
        default_limit = 10
        context = {}
        context['current_season'] = self.get_list_view_data(CurrentSeason)
        context['updates'] = self.get_list_view_data(Updates, default_limit)
        context['populars'] = self.get_list_view_data(Populars, default_limit)
        context['latests'] = self.get_list_view_data(Latests, default_limit)

        return Response(context)


class Sitemap(TemplateView):
    template_name = 'sitemap.xml'
    url = settings.FRONTEND_URL

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response['Content-Type'] = 'text/xml'
        return response

    def _get_url(self, *args) -> str:
        url = '/'.join([self.url, *args])
        if not url.endswith(self.url):
            url += '/'
        return url

    def _get_updates_page(self) -> dict:
        return {
            'url': self._get_url('updates'),
            'lastmod': Episode.objects.filter(
                translation__title=Title.objects.enabled()
                .order_by('-translation__episode__date_created')
                .first()
            )
            .order_by('-date_created')
            .first()
            .date_created.isoformat(),
        }

    def _get_catalog_page(self) -> dict:
        return {
            'url': self._get_url('catalog'),
        }

    def _get_ongoings_page(self) -> dict:
        return {
            'url': self._get_url('ongoings'),
            'lastmod': Episode.objects.filter(
                translation__title=Title.objects.enabled()
                .filter(status=Title.STATUSES.ongoing)
                .order_by('-translation__episode__date_created')[0]
            )
            .order_by('-date_created')[0]
            .date_created.isoformat(),
        }

    def _get_base_page(self) -> dict:
        return {'url': self._get_url()}

    def _get_titles_pages(self) -> list:
        urls = []
        for title in Title.objects.enabled():
            urls.append(
                {
                    'url': self._get_url('title', title.slug),
                    'lastmod': Episode.objects.filter(translation__title=title)
                    .order_by('-date_created')[0]
                    .date_created.isoformat(),
                }
            )
        return urls

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pages'] = [
            self._get_base_page(),
            self._get_updates_page(),
            self._get_catalog_page(),
            self._get_ongoings_page(),
            *self._get_titles_pages(),
        ]

        return context
