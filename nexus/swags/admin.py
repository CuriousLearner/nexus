# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib import admin

# nexus Stuff
from nexus.swags.models import Swag, SwagItem, SwagOwnership


@admin.register(Swag)
class SwagAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Swag Details', {'fields': ('item', 'sponsered_by', 'description', 'image')}),
    )
    list_display = ('item', 'sponsered_by', 'description')


@admin.register(SwagItem)
class SwagItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Swag item details', {'fields': ('name',)}),
    )
    list_display = ('name',)


@admin.register(SwagOwnership)
class UserSwagAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User Swag relationships', {'fields': ('user', 'swag')}),
    )
    list_display = ('user', 'swag')
