# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from guardian.admin import GuardedModelAdmin

from mystery_shopping.users.models import ClientUser

from mystery_shopping.users.models import (
    ClientProjectManager,
    DetractorRespondent,
    Shopper,
    TenantProductManager,
    User
)


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


@admin.register(ClientUser)
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_company', 'job_title')

    def get_company(self, obj):
        return obj.company.element_name

    def get_username(self, obj):
        return obj.user.username

    get_company.short_description = 'Company'
    get_username.short_description = 'Username'


@admin.register(Shopper)
class ShopperAdmin(admin.ModelAdmin):
    pass


@admin.register(DetractorRespondent)
class DetractorRespondentAdmin(admin.ModelAdmin):
    pass
