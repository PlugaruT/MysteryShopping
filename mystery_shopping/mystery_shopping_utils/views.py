class GetSerializerClassMixin:
    """
    Mixin that implements get_serializer_class for a view. It uses 2 serializers based on the request that is used
    """
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class_get
        return self.serializer_class
