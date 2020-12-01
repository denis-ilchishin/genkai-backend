from django.contrib.admin.widgets import AdminFileWidget


class AdminImageWidget(AdminFileWidget):
    class Media:
        js = [
            'js/admin_image.js',
        ]

    template_name = 'widgets/admin_image.html'
