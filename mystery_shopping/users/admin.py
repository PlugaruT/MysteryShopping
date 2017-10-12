# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from guardian.admin import GuardedModelAdmin

from django.utils.translation import ugettext, ugettext_lazy as _
from mystery_shopping.users.models import ClientUser
from .models import User
from .models import TenantProductManager
from .models import TenantProjectManager
from .models import TenantConsultant
from .models import Shopper
from .models import ClientManager
from .models import ClientEmployee
from .models import PersonToAssess
from .models import ClientProjectManager


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class UserAdmin(AuthUserAdmin, GuardedModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tenant',)
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    fieldsets = AuthUserAdmin.fieldsets + (
        (_('Additional info'), {'fields': ('date_of_birth', 'gender', 'tenant', 'phone_number')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('tenant', 'username', 'password1', 'password2', ),
        }),
    )


@admin.register(TenantProductManager, TenantProjectManager, TenantConsultant, ClientProjectManager, ClientManager,
                ClientEmployee, PersonToAssess, ClientUser)
class Tenants(admin.ModelAdmin):
    pass


@admin.register(Shopper)
class ShopperAdmin(admin.ModelAdmin):
    pass
