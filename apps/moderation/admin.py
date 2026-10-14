from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import StaffActionLog

@admin.register(StaffActionLog)
class StaffActionLogAdmin(ModelAdmin):
    list_display = ('staff_user', 'action_type', 'target_reference', 'created_at', 'ip_address')
    list_filter = ('action_type', 'created_at')
    search_fields = ('staff_user__email', 'target_reference', 'details')
    readonly_fields = ('staff_user', 'action_type', 'target_reference', 'details', 'ip_address', 'created_at')
