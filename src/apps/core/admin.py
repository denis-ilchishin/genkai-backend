from django.conf import settings
from django.contrib import admin

from apps.authentication.forms import AdminAuthenticationForm

admin.site.site_header = 'Администрирование сайта Genkai'
admin.site.site_url = settings.FRONTEND_URL
admin.site.login_form = AdminAuthenticationForm
admin.site.login_template = 'admin/login.html'

