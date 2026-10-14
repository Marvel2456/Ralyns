from django.db import models
from apps.core.models import BaseUUIDModel
from apps.accounts.models import CustomUser

class StaffActionLog(BaseUUIDModel):
    """
    Audit log of actions performed by Moderators and Admins.
    """
    staff_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='action_logs')
    action_type = models.CharField(max_length=100) # e.g. "ROUTE_CREATED", "STATUS_UPDATED", "MODERATOR_ADDED"
    target_reference = models.CharField(max_length=255) # e.g. "Route: Guangzhou to Lagos" or "Tracking: RAL-AIR-8921"
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Staff Action Log'
        verbose_name_plural = 'Staff Action Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.staff_user.full_name} - {self.action_type} ({self.created_at:%Y-%m-%d %H:%M})"
