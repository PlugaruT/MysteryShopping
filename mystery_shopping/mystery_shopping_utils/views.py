class GetSerializerClassMixin:
    """
    Mixin that implements get_serializer_class for a view.
    It uses 2 serializers based on the type of request

    !needs to implement serializer_class_get!
    """
    def get_serializer_class(self):
        if self.request.method == 'GET':
            assert self.serializer_class_get is not None, (
                "'%s' should include a `serializer_class_get` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
            )
            return self.serializer_class_get
        return self.serializer_class
