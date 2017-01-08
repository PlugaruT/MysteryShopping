class CreateSerializerMixin:
    def _serializer_create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

class UpdateSerializerMixin:
    def _serializer_update(self, instance, data):
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

