import json
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .models import BuildProject, RoomTemplate
from .exporter import generate_batch_script
from .validators import validate_project


# V5 Room Template Presets
V5_ROOM_TEMPLATES = {
    "elysium": {
        "name": "Elysium",
        "description": "Neutral ground where violence is forbidden. A place of peace among Kindred.",
        "v5": {
            "location_type": "elysium",
            "day_night": "always",
            "danger_level": "safe",
            "hunting_modifier": 0,
        },
    },
    "haven": {
        "name": "Haven",
        "description": "A vampire's personal sanctuary and refuge from the outside world.",
        "v5": {
            "location_type": "haven",
            "day_night": "restricted",
            "danger_level": "low",
            "hunting_modifier": 0,
            "haven_ratings": {
                "security": 3,
                "size": 2,
                "luxury": 2,
                "warding": 1,
                "location_hidden": False,
            },
        },
    },
    "rack": {
        "name": "Rack (Feeding Ground)",
        "description": "A hunting ground where Kindred feed on mortals. Often dangerous.",
        "v5": {
            "location_type": "rack",
            "day_night": "night_only",
            "danger_level": "moderate",
            "hunting_modifier": 2,
        },
    },
    "hostile_territory": {
        "name": "Hostile Territory",
        "description": "Dangerous area controlled by enemies or hostile forces.",
        "v5": {
            "location_type": "hostile",
            "day_night": "restricted",
            "danger_level": "high",
            "hunting_modifier": -2,
        },
    },
    "neutral_ground": {
        "name": "Neutral Ground",
        "description": "Public areas like streets and parks. Generally safe but exposed.",
        "v5": {
            "location_type": "neutral",
            "day_night": "always",
            "danger_level": "low",
            "hunting_modifier": 0,
        },
    },
    "mortal_establishment": {
        "name": "Mortal Establishment",
        "description": "Human businesses like bars, shops, or restaurants.",
        "v5": {
            "location_type": "mortal",
            "day_night": "always",
            "danger_level": "safe",
            "hunting_modifier": 1,
        },
    },
    "supernatural_site": {
        "name": "Supernatural Site",
        "description": "Places of mystical significance or supernatural importance.",
        "v5": {
            "location_type": "supernatural",
            "day_night": "restricted",
            "danger_level": "moderate",
            "hunting_modifier": 0,
        },
    },
    "clear": {
        "name": "Clear Template",
        "description": "Reset all V5 settings to defaults.",
        "v5": {
            "location_type": "",
            "day_night": "always",
            "danger_level": "safe",
            "hunting_modifier": 0,
        },
    },
}


class StaffRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to be staff."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            return HttpResponseForbidden("Builder access requires staff permissions.")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(staff_member_required, name="dispatch")
class BuilderDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard showing all builder projects."""

    template_name = "builder/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # User's own projects
        ctx["my_projects"] = BuildProject.objects.filter(user=self.request.user)
        # Public projects from others
        ctx["public_projects"] = BuildProject.objects.filter(is_public=True).exclude(
            user=self.request.user
        )[:20]
        return ctx


@method_decorator(staff_member_required, name="dispatch")
class BuilderEditorView(LoginRequiredMixin, TemplateView):
    """Main editor interface."""

    template_name = "builder/editor.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project_id = self.kwargs.get("pk")

        if project_id:
            project = get_object_or_404(BuildProject, pk=project_id)
            # Check ownership for editing
            ctx["can_edit"] = project.user == self.request.user
            ctx["project"] = project
            ctx["project_data"] = json.dumps(project.map_data)
            ctx["project_id"] = project.id
            ctx["project_name"] = project.name
        else:
            ctx["can_edit"] = True
            ctx["project"] = None
            ctx["project_data"] = json.dumps(BuildProject().get_default_map_data())
            ctx["project_id"] = None
            ctx["project_name"] = "New Project"

        return ctx


# API views
class SaveProjectView(StaffRequiredMixin, View):
    """Save or create a project."""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "error": "Invalid JSON"}, status=400
            )

        project_id = data.get("id")
        name = data.get("name", "Untitled Project")
        map_data = data.get("map_data", {})

        # Validate project data
        is_valid, errors, warnings = validate_project(map_data)

        if project_id:
            # Update existing
            project = get_object_or_404(BuildProject, pk=project_id)
            if project.user != request.user:
                return JsonResponse(
                    {"status": "error", "error": "Not authorized"}, status=403
                )

            # Optimistic concurrency check
            client_version = data.get("version")
            if client_version is not None and client_version != project.version:
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "Project was modified by another session. Reload and try again.",
                        "server_version": project.version,
                    },
                    status=409,
                )

            project.name = name
            project.map_data = map_data
            project.version = (project.version or 0) + 1
            project.save()
        else:
            # Create new
            project = BuildProject.objects.create(
                user=request.user,
                name=name,
                map_data=map_data,
                version=1,
            )

        return JsonResponse(
            {
                "status": "success",
                "id": project.id,
                "version": project.version,
                "validation": {
                    "is_valid": is_valid,
                    "errors": errors,
                    "warnings": warnings,
                },
            }
        )


class GetProjectView(StaffRequiredMixin, View):
    """Get project data."""

    def get(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Check visibility
        if not project.is_public and project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"}, status=403
            )

        return JsonResponse(
            {
                "status": "success",
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "map_data": project.map_data,
                    "is_public": project.is_public,
                    "sandbox_room_id": project.sandbox_room_id,
                    "can_edit": project.user == request.user,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                },
            }
        )


class DeleteProjectView(StaffRequiredMixin, View):
    """Delete a project."""

    def delete(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        if project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"}, status=403
            )

        project.delete()
        return JsonResponse({"status": "success"})

    def post(self, request, pk, *args, **kwargs):
        # Allow POST as fallback for clients that don't support DELETE
        return self.delete(request, pk, *args, **kwargs)


class BuildProjectView(StaffRequiredMixin, View):
    """Build project to sandbox."""

    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Check ownership - only owner can build
        if project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"}, status=403
            )

        # Check if sandbox already exists
        if project.sandbox_room_id:
            return JsonResponse(
                {
                    "status": "error",
                    "error": "Sandbox already exists. Use @abandon in-game first.",
                    "sandbox_id": project.sandbox_room_id,
                },
                status=400,
            )

        # For now, return manual_required status with download URL
        # Automatic execution requires more integration work
        return JsonResponse(
            {
                "status": "manual_required",
                "message": "Automatic execution not yet implemented. Download and run manually.",
                "download_url": f"/builder/export/{pk}/",
            }
        )


class PrototypesView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


class TemplatesView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "success", "templates": V5_ROOM_TEMPLATES})


class ExportProjectView(StaffRequiredMixin, View):
    """Download project as .ev batch file."""

    def get(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Check visibility
        if not project.is_public and project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"}, status=403
            )

        # Generate script
        script_content = generate_batch_script(project, request.user.username)

        # Return as downloadable file
        filename = f"{project.name.replace(' ', '_')}_build.ev"
        response = HttpResponse(script_content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# Approval Workflow Views


class SubmitProjectView(StaffRequiredMixin, View):
    """Submit a project for staff review."""

    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Only owner can submit their own project
        if project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"}, status=403
            )

        # Validate project is in draft status
        if not project.can_transition_to("submitted"):
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Cannot submit project in '{project.status}' status",
                },
                status=400,
            )

        # Parse optional notes from request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        notes = data.get("notes", "")
        if notes:
            project.submission_notes = notes

        # Submit the project
        try:
            project.submit()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Project submitted for review",
                    "project": {
                        "id": project.id,
                        "name": project.name,
                        "status": project.status,
                    },
                }
            )
        except ValueError as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=400)


@method_decorator(staff_member_required, name="dispatch")
class BuildReviewView(View):
    """Staff review interface - list submitted projects."""

    def get(self, request, *args, **kwargs):
        # Get all projects with submitted status
        projects = BuildProject.objects.filter(status="submitted").select_related(
            "user"
        )

        project_list = []
        for project in projects:
            map_data = project.map_data or {}
            rooms = map_data.get("rooms", {})
            exits = map_data.get("exits", {})

            project_list.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "user": {
                        "id": project.user.id,
                        "username": project.user.username,
                    },
                    "submission_notes": project.submission_notes,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                    "room_count": len(rooms),
                    "exit_count": len(exits),
                }
            )

        return JsonResponse({"status": "success", "projects": project_list})


@method_decorator(staff_member_required, name="dispatch")
class ApproveRejectProjectView(View):
    """Approve or reject a submitted project."""

    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Determine action from URL path
        path = request.path
        is_approve = "/approve/" in path
        is_reject = "/reject/" in path

        if not is_approve and not is_reject:
            return JsonResponse(
                {"status": "error", "error": "Invalid action"}, status=400
            )

        # Check project is in submitted status
        if project.status != "submitted":
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Project is not in submitted status (current: {project.status})",
                },
                status=400,
            )

        if is_approve:
            # Approve the project
            try:
                project.approve(request.user)
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Project approved",
                        "project": {
                            "id": project.id,
                            "name": project.name,
                            "status": project.status,
                            "reviewed_by": request.user.username,
                            "reviewed_at": project.reviewed_at.isoformat(),
                        },
                    }
                )
            except ValueError as e:
                return JsonResponse({"status": "error", "error": str(e)}, status=400)

        else:  # is_reject
            # Parse rejection notes from request body
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                return JsonResponse(
                    {"status": "error", "error": "Invalid JSON"}, status=400
                )

            notes = data.get("notes", "").strip()
            if not notes:
                return JsonResponse(
                    {"status": "error", "error": "Rejection notes are required"},
                    status=400,
                )

            # Reject the project
            try:
                project.reject(request.user, notes)
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Project rejected with feedback",
                        "project": {
                            "id": project.id,
                            "name": project.name,
                            "status": project.status,
                            "rejection_count": project.rejection_count,
                        },
                    }
                )
            except ValueError as e:
                return JsonResponse({"status": "error", "error": str(e)}, status=400)


@method_decorator(staff_member_required, name="dispatch")
class BuildReviewDashboardView(LoginRequiredMixin, TemplateView):
    """Staff review page template view."""

    template_name = "builder/review.html"
