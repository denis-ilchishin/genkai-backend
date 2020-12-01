from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('id', 'email', 'username')
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'username',
                    'is_staff',
                    'is_superuser',
                    'is_active',
                    'last_login',
                    'date_created',
                    'date_modified',
                )
            },
        ),
        (
            _('Группы и доступ'),
            {'classes': ('collapse',), 'fields': ('groups', 'user_permissions'),},
        ),
    )
    inlines = (UserProfileInline,)
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ('last_login', 'date_created', 'date_modified')
