from django.db import models
from django.conf import settings


class BuildProject(models.Model):
    """
    Represents a building project (an area/zone).
    Stores the entire map state as a JSON blob.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="build_projects"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # Stores the entire frontend state: rooms, exits, objects, triggers, coords
    map_data = models.JSONField(default=dict)
    # Visibility to other builders
    is_public = models.BooleanField(default=True)
    # Link to in-game sandbox instance (if built)
    sandbox_room_id = models.IntegerField(null=True, blank=True)
    # When promoted to live
    promoted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

    def get_default_map_data(self):
        """Return empty map data structure."""
        return {
            "rooms": {},
            "exits": {},
            "objects": {},
            "next_room_id": 1,
            "next_exit_id": 1,
            "next_object_id": 1,
        }


class RoomTemplate(models.Model):
    """
    Reusable room templates with pre-configured attributes.
    """
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="room_templates"
    )
    template_data = models.JSONField(default=dict)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (by {self.created_by.username})"
