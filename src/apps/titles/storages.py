from apps.core.storages import ImageStorage


class TitlePosterStorage(ImageStorage):
    ratio = 1.39


class TitleWallpaperStorage(ImageStorage):
    ratio = 0.23
    sizes = (('small', 175), ('medium', 233), ('big', 350))


class TitleWallpaperMobileStorage(ImageStorage):
    ratio = 0.41
    sizes = (('xsmall', 250),)
    default = ('jpeg', '2x', 'xsmall')
