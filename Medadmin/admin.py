from django.contrib import admin
from .models import Messege

@admin.register(Messege)
class MessegeAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date')
    search_fields = ('subject', 'description')
