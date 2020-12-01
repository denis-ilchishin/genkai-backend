# from django.conf import settings

# from apps.titles.models import Title
# from apps.users.models import TitleComment, User

# inputs = {
#     'current_season': {'year': 2020, 'year_season': Title.SEASONS.spring},
#     'login': {
#         'username': {
#             'maxLength': User._meta.get_field(User.USERNAME_FIELD).max_length,
#         },
#         'password': {'maxLength': User._meta.get_field('password').max_length,},
#     },
#     'register': {
#         'email': {'maxLength': User._meta.get_field('email').max_length,},
#         'username': {'maxLength': User._meta.get_field('username').max_length,},
#         'password': {'maxLength': User._meta.get_field('password').max_length,},
#     },
#     'title': {
#         'comment': {'maxLength': TitleComment._meta.get_field('text').max_length}
#     },
#     'profile': {
#         'aboutMyself': {'maxLength': User._meta.get_field('about_myself').max_length},
#     },
#     'search': {
#         'minLength': settings.SEARCH_MIN_LENGTH,
#         'maxLength': settings.SEARCH_MAX_LENGTH,
#     },
# }
