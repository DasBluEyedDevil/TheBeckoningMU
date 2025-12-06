import json
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt

from .models import BuildProject, RoomTemplate


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
        ctx["public_projects"] = BuildProject.objects.filter(
            is_public=True
        ).exclude(user=self.request.user)[:20]
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
            ctx["can_edit"] = (project.user == self.request.user)
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
@method_decorator(csrf_exempt, name="dispatch")
class SaveProjectView(StaffRequiredMixin, View):
    """Save or create a project."""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "error": "Invalid JSON"}, status=400)

        project_id = data.get("id")
        name = data.get("name", "Untitled Project")
        map_data = data.get("map_data", {})

        if project_id:
            # Update existing
            project = get_object_or_404(BuildProject, pk=project_id)
            if project.user != request.user:
                return JsonResponse(
                    {"status": "error", "error": "Not authorized"},
                    status=403
                )
            project.name = name
            project.map_data = map_data
            project.save()
        else:
            # Create new
            project = BuildProject.objects.create(
                user=request.user,
                name=name,
                map_data=map_data
            )

        return JsonResponse({"status": "success", "id": project.id})


class GetProjectView(StaffRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteProjectView(StaffRequiredMixin, View):
    def delete(self, request, pk, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


@method_decorator(csrf_exempt, name="dispatch")
class BuildProjectView(StaffRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


class PrototypesView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


class TemplatesView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


class ExportProjectView(StaffRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)
