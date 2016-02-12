from django.conf import settings

# Wrap our settings dict to provide a nicer interface and default values
class EditorConfig(object):
    # Defaults:

    # Info on how to resize images in the form of (size, width) tuples
    IMAGE_SIZES = [
        ('source', None),
        ('full', 700),
        ('small', 250),
    ]
    # Info on image styles
    IMAGE_STYLES = [
        {
            'class': 'full',
            'size': 'full',
        },
        {
            'class': 'left',
            'size': 'small',
        },
        {
            'class': 'right',
            'size': 'small',
        },
    ]

    def __getattribute__(self, name):
        try:
            return getattr(settings, 'EDITOR_CONFIG')[name]
        except (AttributeError, KeyError):
            return super(EditorConfig, self).__getattribute__(name)

config = EditorConfig()
