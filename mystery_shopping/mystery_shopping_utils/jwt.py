# -*- coding: utf-8 -*-
from mystery_shopping.users.serializers import UserSerializerGET


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializerGET(user).data
    }
