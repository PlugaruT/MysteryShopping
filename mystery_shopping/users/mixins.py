from rest_framework import status
from rest_framework.response import Response


class CreateUserMixin:
    def create(self, request, *args, **kwargs):
        request.data['user']['tenant'] = request.user.tenant.id
        super().create(request, *args, **kwargs)


class DestroyOneToOneUserMixin:
    """
    Mixin for deleting One To One relations of model instance with User model
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if the user is destroyed, cascading deleting is triggered and the current instance will be destroyed
        instance.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
