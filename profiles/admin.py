from django.contrib import admin
from .models import FounderProfile

@admin.register(FounderProfile)
class FounderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'created_at')
    search_fields = ('user__username', 'company_name')
    list_filter = ('created_at', 'revenue_stage', 'funding_stage')
