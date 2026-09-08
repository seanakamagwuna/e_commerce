from cloudinary_storage.storage import StaticHashedCloudinaryStorage


class DirectStaticHashedCloudinaryStorage(StaticHashedCloudinaryStorage):
    """
    Same as StaticHashedCloudinaryStorage, but skips the pre-upload existence
    check against res.cloudinary.com, which is unreachable from this network.
    Uploads always go straight through the upload API instead.
    """

    def _exists_with_etag(self, name, content):
        return False
