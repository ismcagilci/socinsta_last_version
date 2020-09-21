from django.contrib import admin
from .models import * 
# Register your models here.



class LicenseAdmin(admin.ModelAdmin):
    list_display = ("main_user","package","status","created_date")

admin.site.register(License,LicenseAdmin)
admin.site.register(Package)
admin.site.register(Coupon)
admin.site.register(Card)