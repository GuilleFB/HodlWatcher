from storages.backends.s3boto3 import S3Boto3Storage


class S3CustomDomainStorage(S3Boto3Storage):
    """
    This class extends S3Boto3Storage allowing the use of custom domains without cloudfront.

    The main use case is to use a dockerized minio or similar during developoment and S3 in
    production environments. It is necessary because clients (browsers) and the backend can be in
    different networks, i.e, the backend in a docker compose network and the browser in localhost.
    """

    def __init__(self, **settings):
        super().__init__(**settings)
        if self.custom_domain and not self.cloudfront_signer:
            self.public_endpoint = self.custom_domain
            self.private_endpoint = self.endpoint_url
            self.custom_domain = None
            self.public_storage = self.get_public_storage()
        else:
            self.public_endpoint = None

    def get_public_storage(self):
        settings = {key: getattr(self, key, def_val) for key, def_val in self.get_default_settings().items()}
        settings["custom_domain"] = None
        settings["endpoint_url"] = self.public_endpoint
        return self.__class__(**settings)

    def url(self, name, parameters=None, expire=None, http_method=None):
        if self.public_endpoint:
            return self.public_storage.url(name, parameters, expire, http_method)
        return super().url(name, parameters, expire, http_method)
