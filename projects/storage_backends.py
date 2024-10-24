from whitenoise.storage import CompressedManifestStaticFilesStorage

class CompressedManifestMediaStorage(CompressedManifestStaticFilesStorage):
    """
    Custom storage backend for serving media files using Whitenoise.
    This is only recommended for small-scale media usage.
    """
    def url(self, name, *args, **kwargs):
        return super().url(name, *args, **kwargs)
