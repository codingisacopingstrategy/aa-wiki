from django.contrib import admin
from models import Page


class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "content")
    search_fields = ("name", "content")
admin.site.register(Page, PageAdmin)
