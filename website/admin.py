from django.contrib import admin

from website.models import *


# Register your models here.
@admin.register(WebSite)
class WebSiteAdmin(admin.ModelAdmin):
    pass


@admin.register(OwnSite)
class OwnSiteAdmin(admin.ModelAdmin):
    pass


@admin.register(AutoLogin)
class AutoLoginAdmin(admin.ModelAdmin):
    pass


@admin.register(SignIn)
class SignInAdmin(admin.ModelAdmin):
    pass
