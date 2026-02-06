# Web Builder Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a web-based visual builder that allows staff to design MUSH areas through a grid interface, generating Evennia batch scripts for staged deployment.

**Architecture:** Django app (`web/builder/`) with REST API endpoints, JSON-based project storage, and batch script exporter. Frontend uses vanilla JavaScript with Bootstrap 5 dark theme. Staged workflow: build to sandbox, verify in-game, promote to live.

**Tech Stack:** Django 4.x, Evennia 4.x, Bootstrap 5.1.3, vanilla JavaScript, HTML5 Canvas for grid

---

## Phase 1: Foundation

### Task 1.1: Create V5 Location Constants

**Files:**
- Create: `beckonmu/world/v5_locations.py`

**Step 1: Create the constants file**

```python
"""
V5 location type constants for the Web Builder.
"""

LOCATION_TYPES = [
    ("haven", "Haven"),
    ("elysium", "Elysium"),
    ("rack", "Rack (Feeding Ground)"),
    ("hostile", "Hostile Territory"),
    ("neutral", "Neutral Ground"),
    ("mortal", "Mortal Establishment"),
    ("supernatural", "Supernatural Site"),
]

DAY_NIGHT_ACCESS = [
    ("always", "Always Accessible"),
    ("day_only", "Day Only (Mortals)"),
    ("night_only", "Night Only"),
    ("restricted", "Restricted Access"),
]

DANGER_LEVELS = [
    ("safe", "Safe"),
    ("low", "Low Risk"),
    ("moderate", "Moderate Risk"),
    ("high", "High Risk"),
    ("deadly", "Deadly"),
]

HAVEN_RATINGS = [
    ("security", "Security"),
    ("size", "Size"),
    ("luxury", "Luxury"),
    ("warding", "Warding"),
    ("location_hidden", "Hidden Location"),
]

# Trigger events for the builder
TRIGGER_EVENTS = [
    ("on_enter", "On Enter"),
    ("on_exit", "On Exit"),
    ("on_look", "On Look"),
    ("on_examine", "On Examine"),
    ("on_time", "On Time"),
]

# Trigger actions for the builder
TRIGGER_ACTIONS = [
    ("message", "Message to Character"),
    ("message_room", "Message to Room"),
    ("reveal_exit", "Reveal Exit"),
    ("hide_exit", "Hide Exit"),
    ("set_flag", "Set Flag"),
    ("check_flag", "Check Flag"),
]
```

**Step 2: Commit**

```bash
git add beckonmu/world/v5_locations.py
git commit -m "feat(builder): add V5 location constants"
```

---

### Task 1.2: Create Builder Django App Structure

**Files:**
- Create: `beckonmu/web/builder/__init__.py`
- Create: `beckonmu/web/builder/apps.py`

**Step 1: Create app directory and __init__.py**

Create empty file: `beckonmu/web/builder/__init__.py`

**Step 2: Create apps.py**

```python
from django.apps import AppConfig


class BuilderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "beckonmu.web.builder"
    verbose_name = "Web Builder"
```

**Step 3: Commit**

```bash
git add beckonmu/web/builder/
git commit -m "feat(builder): create Django app structure"
```

---

### Task 1.3: Create BuildProject Model

**Files:**
- Create: `beckonmu/web/builder/models.py`

**Step 1: Create the models file**

```python
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
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/models.py
git commit -m "feat(builder): add BuildProject and RoomTemplate models"
```

---

### Task 1.4: Register App in Settings

**Files:**
- Modify: `beckonmu/server/conf/settings.py`

**Step 1: Add builder app to INSTALLED_APPS**

Find the `INSTALLED_APPS` section (around line 46-52) and add the builder app:

```python
INSTALLED_APPS = INSTALLED_APPS + [
    "beckonmu.web.bbs",
    "beckonmu.web.jobs",
    "beckonmu.web.status",
    "beckonmu.traits",
    "beckonmu.boons",
    "beckonmu.web.builder",  # Add this line
]
```

**Step 2: Commit**

```bash
git add beckonmu/server/conf/settings.py
git commit -m "feat(builder): register builder app in settings"
```

---

### Task 1.5: Create and Run Migrations

**Files:**
- Create: `beckonmu/web/builder/migrations/__init__.py`
- Create: `beckonmu/web/builder/migrations/0001_initial.py` (auto-generated)

**Step 1: Create migrations directory**

Create empty file: `beckonmu/web/builder/migrations/__init__.py`

**Step 2: Generate migrations**

Run:
```bash
cd C:\Users\dasbl\PycharmProjects\TheBeckoningMU
evennia makemigrations builder
```

Expected: Creates `0001_initial.py` with BuildProject and RoomTemplate

**Step 3: Apply migrations**

Run:
```bash
evennia migrate
```

Expected: "Applying builder.0001_initial... OK"

**Step 4: Commit**

```bash
git add beckonmu/web/builder/migrations/
git commit -m "feat(builder): add initial database migrations"
```

---

### Task 1.6: Create Admin Registration

**Files:**
- Create: `beckonmu/web/builder/admin.py`

**Step 1: Create admin.py**

```python
from django.contrib import admin
from .models import BuildProject, RoomTemplate


@admin.register(BuildProject)
class BuildProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_public", "sandbox_room_id", "updated_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(RoomTemplate)
class RoomTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "is_shared", "created_at"]
    list_filter = ["is_shared"]
    search_fields = ["name", "created_by__username"]
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/admin.py
git commit -m "feat(builder): add Django admin registration"
```

---

## Phase 2: URL Routing and Basic Views

### Task 2.1: Create Builder URLs

**Files:**
- Create: `beckonmu/web/builder/urls.py`

**Step 1: Create urls.py**

```python
from django.urls import path
from . import views

app_name = "builder"

urlpatterns = [
    # Dashboard
    path("", views.BuilderDashboardView.as_view(), name="dashboard"),
    # Editor
    path("edit/", views.BuilderEditorView.as_view(), name="create_project"),
    path("edit/<int:pk>/", views.BuilderEditorView.as_view(), name="edit_project"),
    # API endpoints
    path("api/save/", views.SaveProjectView.as_view(), name="save_project"),
    path("api/project/<int:pk>/", views.GetProjectView.as_view(), name="get_project"),
    path("api/project/<int:pk>/delete/", views.DeleteProjectView.as_view(), name="delete_project"),
    path("api/build/<int:pk>/", views.BuildProjectView.as_view(), name="build_project"),
    path("api/prototypes/", views.PrototypesView.as_view(), name="prototypes"),
    path("api/templates/", views.TemplatesView.as_view(), name="templates"),
    # Export
    path("export/<int:pk>/", views.ExportProjectView.as_view(), name="export_project"),
]
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/urls.py
git commit -m "feat(builder): add URL routing"
```

---

### Task 2.2: Create Base Views

**Files:**
- Create: `beckonmu/web/builder/views.py`

**Step 1: Create views.py with base classes and dashboard**

```python
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


# Placeholder views - will be implemented in later tasks
@method_decorator(csrf_exempt, name="dispatch")
class SaveProjectView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        return JsonResponse({"status": "not_implemented"}, status=501)


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
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/views.py
git commit -m "feat(builder): add base views with placeholders"
```

---

### Task 2.3: Wire Builder URLs to Main Router

**Files:**
- Modify: `beckonmu/web/urls.py`

**Step 1: Add builder URL include**

Find the urlpatterns and add the builder include. The file should look like:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path("builder/", include("beckonmu.web.builder.urls", namespace="builder")),
]
```

Add the builder line after the existing includes but before the evennia default patterns.

**Step 2: Commit**

```bash
git add beckonmu/web/urls.py
git commit -m "feat(builder): wire builder URLs to main router"
```

---

## Phase 3: Templates

### Task 3.1: Create Dashboard Template

**Files:**
- Create: `beckonmu/web/templates/builder/dashboard.html`

**Step 1: Create the template**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Web Builder - Dashboard{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row mb-4">
        <div class="col">
            <h2 class="text-light">Web Builder</h2>
            <p class="text-muted">Create and manage building projects</p>
        </div>
        <div class="col-auto">
            <a href="{% url 'builder:create_project' %}" class="btn btn-danger">
                + New Project
            </a>
        </div>
    </div>

    <!-- My Projects -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-light">My Projects</h5>
                </div>
                <div class="card-body">
                    {% if my_projects %}
                    <div class="table-responsive">
                        <table class="table table-dark table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Rooms</th>
                                    <th>Status</th>
                                    <th>Last Updated</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for project in my_projects %}
                                <tr>
                                    <td>
                                        <a href="{% url 'builder:edit_project' project.pk %}" class="text-danger">
                                            {{ project.name }}
                                        </a>
                                    </td>
                                    <td>{{ project.map_data.rooms|length|default:0 }}</td>
                                    <td>
                                        {% if project.promoted_at %}
                                        <span class="badge bg-success">Live</span>
                                        {% elif project.sandbox_room_id %}
                                        <span class="badge bg-warning text-dark">In Sandbox</span>
                                        {% else %}
                                        <span class="badge bg-secondary">Draft</span>
                                        {% endif %}
                                    </td>
                                    <td>{{ project.updated_at|date:"M d, Y H:i" }}</td>
                                    <td>
                                        <a href="{% url 'builder:edit_project' project.pk %}"
                                           class="btn btn-sm btn-outline-light">Edit</a>
                                        <a href="{% url 'builder:export_project' project.pk %}"
                                           class="btn btn-sm btn-outline-secondary">Export</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <p class="text-muted mb-0">No projects yet. Create your first one!</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <!-- Public Projects -->
    {% if public_projects %}
    <div class="row">
        <div class="col-12">
            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-light">Public Projects (View Only)</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-dark table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Author</th>
                                    <th>Rooms</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for project in public_projects %}
                                <tr>
                                    <td>{{ project.name }}</td>
                                    <td>{{ project.user.username }}</td>
                                    <td>{{ project.map_data.rooms|length|default:0 }}</td>
                                    <td>
                                        <a href="{% url 'builder:edit_project' project.pk %}"
                                           class="btn btn-sm btn-outline-secondary">View</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
```

**Step 2: Commit**

```bash
git add beckonmu/web/templates/builder/dashboard.html
git commit -m "feat(builder): add dashboard template"
```

---

### Task 3.2: Create Editor Template (Part 1 - Structure)

**Files:**
- Create: `beckonmu/web/templates/builder/editor.html`

**Step 1: Create editor template with HTML structure**

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Web Builder - {{ project_name }}{% endblock %}

{% block extra_css %}
<style>
    :root {
        --builder-bg: #1a1a1a;
        --builder-panel: #222;
        --builder-border: #444;
        --builder-accent: #8b0000;
        --builder-text: #eee;
        --builder-muted: #888;
    }

    .builder-container {
        display: flex;
        height: calc(100vh - 56px);
        background: var(--builder-bg);
    }

    /* Sidebar */
    .builder-sidebar {
        width: 320px;
        background: var(--builder-panel);
        border-right: 1px solid var(--builder-border);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .sidebar-header {
        padding: 15px;
        border-bottom: 1px solid var(--builder-border);
    }

    .sidebar-content {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
    }

    .sidebar-footer {
        padding: 15px;
        border-top: 1px solid var(--builder-border);
    }

    /* Canvas Area */
    .canvas-area {
        flex: 1;
        position: relative;
        overflow: hidden;
        background-color: var(--builder-bg);
        background-image: radial-gradient(var(--builder-border) 1px, transparent 1px);
        background-size: 20px 20px;
    }

    .canvas-toolbar {
        position: absolute;
        top: 10px;
        left: 10px;
        display: flex;
        gap: 5px;
        z-index: 100;
    }

    .canvas-info {
        position: absolute;
        bottom: 10px;
        left: 10px;
        background: var(--builder-panel);
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        color: var(--builder-muted);
    }

    /* Room Nodes */
    .room-node {
        position: absolute;
        width: 80px;
        height: 60px;
        background: #444;
        border: 2px solid #666;
        border-radius: 5px;
        cursor: move;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--builder-text);
        font-size: 11px;
        text-align: center;
        padding: 5px;
        user-select: none;
        transition: border-color 0.15s, background 0.15s;
    }

    .room-node:hover {
        border-color: #888;
    }

    .room-node.selected {
        border-color: var(--builder-accent);
        background: #4a2020;
    }

    /* Exit Lines */
    .exit-line {
        position: absolute;
        pointer-events: none;
        z-index: 1;
    }

    /* Property Sections */
    .prop-section {
        margin-bottom: 15px;
    }

    .prop-section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        padding: 8px 0;
        border-bottom: 1px solid var(--builder-border);
        color: var(--builder-text);
    }

    .prop-section-header:hover {
        color: var(--builder-accent);
    }

    .prop-section-content {
        padding-top: 10px;
    }

    .prop-section-content.collapsed {
        display: none;
    }

    /* Form Controls */
    .builder-input {
        background: var(--builder-bg);
        border: 1px solid var(--builder-border);
        color: var(--builder-text);
        padding: 6px 10px;
        border-radius: 4px;
        width: 100%;
    }

    .builder-input:focus {
        outline: none;
        border-color: var(--builder-accent);
    }

    .builder-select {
        background: var(--builder-bg);
        border: 1px solid var(--builder-border);
        color: var(--builder-text);
        padding: 6px 10px;
        border-radius: 4px;
        width: 100%;
    }

    .builder-textarea {
        background: var(--builder-bg);
        border: 1px solid var(--builder-border);
        color: var(--builder-text);
        padding: 6px 10px;
        border-radius: 4px;
        width: 100%;
        min-height: 80px;
        resize: vertical;
    }

    .builder-label {
        display: block;
        color: var(--builder-muted);
        font-size: 12px;
        margin-bottom: 4px;
    }

    .form-group {
        margin-bottom: 12px;
    }

    /* Mode buttons */
    .mode-btn {
        padding: 6px 12px;
        background: var(--builder-panel);
        border: 1px solid var(--builder-border);
        color: var(--builder-text);
        border-radius: 4px;
        cursor: pointer;
    }

    .mode-btn:hover {
        background: #333;
    }

    .mode-btn.active {
        background: var(--builder-accent);
        border-color: var(--builder-accent);
    }

    /* Status bar */
    .status-bar {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 30px;
        background: var(--builder-panel);
        border-top: 1px solid var(--builder-border);
        display: flex;
        align-items: center;
        padding: 0 15px;
        font-size: 12px;
        color: var(--builder-muted);
    }

    .status-item {
        margin-right: 20px;
    }

    /* No selection message */
    .no-selection {
        color: var(--builder-muted);
        text-align: center;
        padding: 40px 20px;
    }
</style>
{% endblock %}

{% block content %}
<div class="builder-container">
    <!-- Sidebar -->
    <div class="builder-sidebar">
        <div class="sidebar-header">
            <input type="text" id="project-name" class="builder-input"
                   value="{{ project_name }}" placeholder="Project Name"
                   {% if not can_edit %}disabled{% endif %}>
        </div>

        <div class="sidebar-content">
            <div id="no-selection" class="no-selection">
                <p>Select a room to edit its properties</p>
                <p class="small">or click "+ Room" to create one</p>
            </div>

            <div id="room-properties" style="display: none;">
                <!-- Basic Section -->
                <div class="prop-section">
                    <div class="prop-section-header" onclick="toggleSection(this)">
                        <span>Basic</span>
                        <span class="toggle-icon">-</span>
                    </div>
                    <div class="prop-section-content">
                        <div class="form-group">
                            <label class="builder-label">Name</label>
                            <input type="text" id="room-name" class="builder-input"
                                   placeholder="Room Name">
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Description</label>
                            <textarea id="room-desc" class="builder-textarea"
                                      placeholder="Room description..."></textarea>
                        </div>
                    </div>
                </div>

                <!-- V5 Settings Section -->
                <div class="prop-section">
                    <div class="prop-section-header" onclick="toggleSection(this)">
                        <span>V5 Settings</span>
                        <span class="toggle-icon">-</span>
                    </div>
                    <div class="prop-section-content">
                        <div class="form-group">
                            <label class="builder-label">Location Type</label>
                            <select id="room-location-type" class="builder-select">
                                <option value="">-- None --</option>
                                <option value="haven">Haven</option>
                                <option value="elysium">Elysium</option>
                                <option value="rack">Rack (Feeding Ground)</option>
                                <option value="hostile">Hostile Territory</option>
                                <option value="neutral">Neutral Ground</option>
                                <option value="mortal">Mortal Establishment</option>
                                <option value="supernatural">Supernatural Site</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Day/Night Access</label>
                            <select id="room-day-night" class="builder-select">
                                <option value="always">Always Accessible</option>
                                <option value="day_only">Day Only (Mortals)</option>
                                <option value="night_only">Night Only</option>
                                <option value="restricted">Restricted Access</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Danger Level</label>
                            <select id="room-danger" class="builder-select">
                                <option value="safe">Safe</option>
                                <option value="low">Low Risk</option>
                                <option value="moderate">Moderate Risk</option>
                                <option value="high">High Risk</option>
                                <option value="deadly">Deadly</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Hunting Modifier</label>
                            <input type="number" id="room-hunting" class="builder-input"
                                   value="0" min="-5" max="5">
                        </div>
                    </div>
                </div>

                <!-- Haven Ratings Section (shown when location_type is haven) -->
                <div class="prop-section" id="haven-section" style="display: none;">
                    <div class="prop-section-header" onclick="toggleSection(this)">
                        <span>Haven Ratings</span>
                        <span class="toggle-icon">-</span>
                    </div>
                    <div class="prop-section-content">
                        <div class="form-group">
                            <label class="builder-label">Security (0-5)</label>
                            <input type="number" id="haven-security" class="builder-input"
                                   value="0" min="0" max="5">
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Size (0-5)</label>
                            <input type="number" id="haven-size" class="builder-input"
                                   value="0" min="0" max="5">
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Luxury (0-5)</label>
                            <input type="number" id="haven-luxury" class="builder-input"
                                   value="0" min="0" max="5">
                        </div>
                        <div class="form-group">
                            <label class="builder-label">Warding (0-5)</label>
                            <input type="number" id="haven-warding" class="builder-input"
                                   value="0" min="0" max="5">
                        </div>
                        <div class="form-group">
                            <label class="builder-label">
                                <input type="checkbox" id="haven-hidden"> Hidden Location
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Triggers Section -->
                <div class="prop-section">
                    <div class="prop-section-header" onclick="toggleSection(this)">
                        <span>Triggers (<span id="trigger-count">0</span>)</span>
                        <span class="toggle-icon">-</span>
                    </div>
                    <div class="prop-section-content">
                        <div id="triggers-list"></div>
                        <button class="btn btn-sm btn-outline-secondary w-100 mt-2"
                                onclick="addTrigger()">+ Add Trigger</button>
                    </div>
                </div>

                <!-- Builder Notes Section -->
                <div class="prop-section">
                    <div class="prop-section-header" onclick="toggleSection(this)">
                        <span>Builder Notes</span>
                        <span class="toggle-icon">-</span>
                    </div>
                    <div class="prop-section-content">
                        <textarea id="room-notes" class="builder-textarea"
                                  placeholder="Private notes..."></textarea>
                    </div>
                </div>

                <!-- Delete Button -->
                <button class="btn btn-outline-danger w-100 mt-3" onclick="deleteSelected()">
                    Delete Room
                </button>
            </div>
        </div>

        <div class="sidebar-footer">
            {% if can_edit %}
            <button class="btn btn-danger w-100 mb-2" onclick="saveProject()">
                Save Project
            </button>
            <button class="btn btn-outline-success w-100" onclick="buildToSandbox()">
                Build to Sandbox
            </button>
            {% else %}
            <div class="alert alert-secondary mb-0 py-2 text-center">
                View Only Mode
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Canvas -->
    <div class="canvas-area" id="map-canvas">
        <div class="canvas-toolbar">
            <button class="mode-btn active" id="mode-select" onclick="setMode('select')">
                Select
            </button>
            <button class="mode-btn" id="mode-room" onclick="setMode('room')">
                + Room
            </button>
            <button class="mode-btn" id="mode-exit" onclick="setMode('exit')">
                + Exit
            </button>
            <button class="mode-btn" id="mode-compass" onclick="setMode('compass')">
                Compass
            </button>
        </div>

        <svg id="exit-lines" class="exit-line" style="width: 100%; height: 100%;"></svg>

        <div class="status-bar">
            <span class="status-item">Rooms: <span id="room-count">0</span></span>
            <span class="status-item">Exits: <span id="exit-count">0</span></span>
            <span class="status-item">Mode: <span id="current-mode">Select</span></span>
            <span class="status-item" id="save-status"></span>
        </div>
    </div>
</div>

<script>
    // Project data
    let projectId = {{ project_id|default:"null" }};
    let canEdit = {{ can_edit|yesno:"true,false" }};
    let mapData = {{ project_data|safe }};

    // Editor state
    let selectedRoomId = null;
    let currentMode = 'select';
    let exitSourceRoom = null;

    // Grid settings
    const GRID_SIZE = 20;
    const ROOM_WIDTH = 80;
    const ROOM_HEIGHT = 60;

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        initMap();
        updateStatusBar();
    });

    function initMap() {
        // Clear existing nodes
        document.querySelectorAll('.room-node').forEach(el => el.remove());

        // Create room nodes
        if (mapData.rooms) {
            for (const [id, room] of Object.entries(mapData.rooms)) {
                createRoomElement(id, room);
            }
        }

        // Draw exit lines
        drawExitLines();
    }

    function createRoomElement(id, room) {
        const el = document.createElement('div');
        el.className = 'room-node';
        el.id = `room-${id}`;
        el.style.left = (room.grid_x * GRID_SIZE) + 'px';
        el.style.top = (room.grid_y * GRID_SIZE) + 'px';
        el.innerText = room.name || 'New Room';

        // Click handler
        el.addEventListener('mousedown', function(e) {
            if (currentMode === 'select') {
                selectRoom(id);
                if (canEdit) startDrag(e, el, id);
            } else if (currentMode === 'exit') {
                handleExitClick(id);
            }
        });

        document.getElementById('map-canvas').appendChild(el);
    }

    function selectRoom(id) {
        // Deselect previous
        if (selectedRoomId) {
            const prev = document.getElementById(`room-${selectedRoomId}`);
            if (prev) prev.classList.remove('selected');
        }

        selectedRoomId = id;
        document.getElementById(`room-${id}`).classList.add('selected');

        // Show properties panel
        document.getElementById('no-selection').style.display = 'none';
        document.getElementById('room-properties').style.display = 'block';

        // Populate fields
        const room = mapData.rooms[id];
        document.getElementById('room-name').value = room.name || '';
        document.getElementById('room-desc').value = room.description || '';
        document.getElementById('room-notes').value = room.builder_notes || '';

        // V5 settings
        const v5 = room.v5 || {};
        document.getElementById('room-location-type').value = v5.location_type || '';
        document.getElementById('room-day-night').value = v5.day_night || 'always';
        document.getElementById('room-danger').value = v5.danger_level || 'safe';
        document.getElementById('room-hunting').value = v5.hunting_modifier || 0;

        // Show/hide haven section
        toggleHavenSection(v5.location_type === 'haven');

        if (v5.haven_ratings) {
            document.getElementById('haven-security').value = v5.haven_ratings.security || 0;
            document.getElementById('haven-size').value = v5.haven_ratings.size || 0;
            document.getElementById('haven-luxury').value = v5.haven_ratings.luxury || 0;
            document.getElementById('haven-warding').value = v5.haven_ratings.warding || 0;
            document.getElementById('haven-hidden').checked = v5.haven_ratings.location_hidden || false;
        }

        // Triggers
        updateTriggersDisplay(room.triggers || []);

        // Bind input handlers
        bindRoomInputs(id);
    }

    function bindRoomInputs(id) {
        const room = mapData.rooms[id];

        document.getElementById('room-name').oninput = function(e) {
            room.name = e.target.value;
            document.getElementById(`room-${id}`).innerText = e.target.value || 'New Room';
        };

        document.getElementById('room-desc').oninput = function(e) {
            room.description = e.target.value;
        };

        document.getElementById('room-notes').oninput = function(e) {
            room.builder_notes = e.target.value;
        };

        document.getElementById('room-location-type').onchange = function(e) {
            if (!room.v5) room.v5 = {};
            room.v5.location_type = e.target.value;
            toggleHavenSection(e.target.value === 'haven');
        };

        document.getElementById('room-day-night').onchange = function(e) {
            if (!room.v5) room.v5 = {};
            room.v5.day_night = e.target.value;
        };

        document.getElementById('room-danger').onchange = function(e) {
            if (!room.v5) room.v5 = {};
            room.v5.danger_level = e.target.value;
        };

        document.getElementById('room-hunting').onchange = function(e) {
            if (!room.v5) room.v5 = {};
            room.v5.hunting_modifier = parseInt(e.target.value) || 0;
        };
    }

    function toggleHavenSection(show) {
        document.getElementById('haven-section').style.display = show ? 'block' : 'none';
    }

    function toggleSection(header) {
        const content = header.nextElementSibling;
        const icon = header.querySelector('.toggle-icon');

        if (content.classList.contains('collapsed')) {
            content.classList.remove('collapsed');
            icon.textContent = '-';
        } else {
            content.classList.add('collapsed');
            icon.textContent = '+';
        }
    }

    function setMode(mode) {
        currentMode = mode;
        exitSourceRoom = null;

        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`mode-${mode}`).classList.add('active');

        // Update status
        const modeNames = {select: 'Select', room: 'Add Room', exit: 'Add Exit', compass: 'Compass'};
        document.getElementById('current-mode').textContent = modeNames[mode];

        // Canvas click handler
        const canvas = document.getElementById('map-canvas');
        if (mode === 'room') {
            canvas.style.cursor = 'crosshair';
            canvas.onclick = function(e) {
                if (e.target === canvas || e.target.id === 'exit-lines') {
                    addRoomAt(e.clientX, e.clientY);
                }
            };
        } else {
            canvas.style.cursor = 'default';
            canvas.onclick = null;
        }
    }

    function addRoomAt(clientX, clientY) {
        if (!canEdit) return;

        const canvas = document.getElementById('map-canvas');
        const rect = canvas.getBoundingClientRect();

        // Snap to grid
        let x = Math.round((clientX - rect.left) / GRID_SIZE) * GRID_SIZE;
        let y = Math.round((clientY - rect.top) / GRID_SIZE) * GRID_SIZE;

        // Convert to grid units
        const gridX = Math.floor(x / GRID_SIZE);
        const gridY = Math.floor(y / GRID_SIZE);

        // Create room
        const id = 'r' + (mapData.next_room_id || 1);
        mapData.next_room_id = (mapData.next_room_id || 1) + 1;

        if (!mapData.rooms) mapData.rooms = {};

        mapData.rooms[id] = {
            name: 'New Room',
            description: '',
            grid_x: gridX,
            grid_y: gridY,
            v5: {
                location_type: '',
                day_night: 'always',
                danger_level: 'safe',
                hunting_modifier: 0
            },
            triggers: [],
            builder_notes: ''
        };

        createRoomElement(id, mapData.rooms[id]);
        selectRoom(id);
        updateStatusBar();
    }

    function deleteSelected() {
        if (!canEdit || !selectedRoomId) return;

        if (!confirm('Delete this room and all its exits?')) return;

        // Remove exits connected to this room
        if (mapData.exits) {
            for (const [exitId, exit] of Object.entries(mapData.exits)) {
                if (exit.source === selectedRoomId || exit.target === selectedRoomId) {
                    delete mapData.exits[exitId];
                }
            }
        }

        // Remove room
        delete mapData.rooms[selectedRoomId];
        document.getElementById(`room-${selectedRoomId}`).remove();

        // Clear selection
        selectedRoomId = null;
        document.getElementById('no-selection').style.display = 'block';
        document.getElementById('room-properties').style.display = 'none';

        drawExitLines();
        updateStatusBar();
    }

    function handleExitClick(roomId) {
        if (!canEdit) return;

        if (!exitSourceRoom) {
            exitSourceRoom = roomId;
            document.getElementById(`room-${roomId}`).style.borderColor = '#0f0';
        } else if (exitSourceRoom !== roomId) {
            // Create exit
            createExit(exitSourceRoom, roomId);
            document.getElementById(`room-${exitSourceRoom}`).style.borderColor = '';
            exitSourceRoom = null;
        }
    }

    function createExit(sourceId, targetId) {
        const id = 'e' + (mapData.next_exit_id || 1);
        mapData.next_exit_id = (mapData.next_exit_id || 1) + 1;

        if (!mapData.exits) mapData.exits = {};

        mapData.exits[id] = {
            name: 'exit',
            aliases: [],
            source: sourceId,
            target: targetId,
            description: '',
            locks: ''
        };

        drawExitLines();
        updateStatusBar();
    }

    function drawExitLines() {
        const svg = document.getElementById('exit-lines');
        svg.innerHTML = '';

        if (!mapData.exits) return;

        for (const [id, exit] of Object.entries(mapData.exits)) {
            const sourceRoom = mapData.rooms[exit.source];
            const targetRoom = mapData.rooms[exit.target];

            if (!sourceRoom || !targetRoom) continue;

            const x1 = sourceRoom.grid_x * GRID_SIZE + ROOM_WIDTH / 2;
            const y1 = sourceRoom.grid_y * GRID_SIZE + ROOM_HEIGHT / 2;
            const x2 = targetRoom.grid_x * GRID_SIZE + ROOM_WIDTH / 2;
            const y2 = targetRoom.grid_y * GRID_SIZE + ROOM_HEIGHT / 2;

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x1);
            line.setAttribute('y1', y1);
            line.setAttribute('x2', x2);
            line.setAttribute('y2', y2);
            line.setAttribute('stroke', '#666');
            line.setAttribute('stroke-width', '2');

            svg.appendChild(line);
        }
    }

    function startDrag(e, el, roomId) {
        if (!canEdit) return;

        const canvas = document.getElementById('map-canvas');
        const rect = canvas.getBoundingClientRect();
        const startX = e.clientX;
        const startY = e.clientY;
        const startLeft = parseInt(el.style.left);
        const startTop = parseInt(el.style.top);

        function onMove(e) {
            let newX = startLeft + (e.clientX - startX);
            let newY = startTop + (e.clientY - startY);

            // Snap to grid
            newX = Math.round(newX / GRID_SIZE) * GRID_SIZE;
            newY = Math.round(newY / GRID_SIZE) * GRID_SIZE;

            el.style.left = newX + 'px';
            el.style.top = newY + 'px';

            mapData.rooms[roomId].grid_x = Math.floor(newX / GRID_SIZE);
            mapData.rooms[roomId].grid_y = Math.floor(newY / GRID_SIZE);

            drawExitLines();
        }

        function onUp() {
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        }

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    }

    function updateStatusBar() {
        document.getElementById('room-count').textContent =
            Object.keys(mapData.rooms || {}).length;
        document.getElementById('exit-count').textContent =
            Object.keys(mapData.exits || {}).length;
    }

    function updateTriggersDisplay(triggers) {
        document.getElementById('trigger-count').textContent = triggers.length;
        // TODO: Implement trigger list UI
    }

    function addTrigger() {
        // TODO: Implement trigger creation UI
        alert('Trigger editor coming in Phase 5');
    }

    async function saveProject() {
        if (!canEdit) return;

        const name = document.getElementById('project-name').value || 'Untitled Project';

        document.getElementById('save-status').textContent = 'Saving...';

        try {
            const response = await fetch("{% url 'builder:save_project' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({
                    id: projectId,
                    name: name,
                    map_data: mapData
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                projectId = result.id;
                document.getElementById('save-status').textContent = 'Saved!';
                setTimeout(() => {
                    document.getElementById('save-status').textContent = '';
                }, 2000);
            } else {
                document.getElementById('save-status').textContent = 'Error: ' + result.error;
            }
        } catch (err) {
            document.getElementById('save-status').textContent = 'Error: ' + err.message;
        }
    }

    function buildToSandbox() {
        if (!canEdit || !projectId) {
            alert('Please save the project first.');
            return;
        }
        alert('Build to Sandbox coming in Phase 6');
    }
</script>
{% endblock %}
```

**Step 2: Commit**

```bash
git add beckonmu/web/templates/builder/editor.html
git commit -m "feat(builder): add editor template with grid canvas"
```

---

## Phase 4: API Implementation

### Task 4.1: Implement Save Project API

**Files:**
- Modify: `beckonmu/web/builder/views.py`

**Step 1: Update SaveProjectView**

Replace the placeholder `SaveProjectView` with:

```python
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
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/views.py
git commit -m "feat(builder): implement save project API"
```

---

### Task 4.2: Implement Get and Delete Project APIs

**Files:**
- Modify: `beckonmu/web/builder/views.py`

**Step 1: Update GetProjectView**

```python
class GetProjectView(StaffRequiredMixin, View):
    """Get project data."""

    def get(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Check visibility
        if not project.is_public and project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"},
                status=403
            )

        return JsonResponse({
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
            }
        })
```

**Step 2: Update DeleteProjectView**

```python
@method_decorator(csrf_exempt, name="dispatch")
class DeleteProjectView(StaffRequiredMixin, View):
    """Delete a project."""

    def delete(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        if project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"},
                status=403
            )

        project.delete()
        return JsonResponse({"status": "success"})

    def post(self, request, pk, *args, **kwargs):
        # Allow POST as fallback for clients that don't support DELETE
        return self.delete(request, pk, *args, **kwargs)
```

**Step 3: Commit**

```bash
git add beckonmu/web/builder/views.py
git commit -m "feat(builder): implement get and delete project APIs"
```

---

## Phase 5: Batch Script Exporter

### Task 5.1: Create Exporter Module

**Files:**
- Create: `beckonmu/web/builder/exporter.py`

**Step 1: Create the exporter**

```python
"""
Batch script exporter for the Web Builder.
Converts JSON map data to Evennia .ev batch command format.
"""
import re
from datetime import datetime


def sanitize_string(value):
    """
    Sanitize a string for safe inclusion in batch commands.
    Removes/escapes characters that could break command parsing.
    """
    if not value:
        return ""
    # Remove problematic characters
    value = str(value)
    # Escape any @ at start of lines (could be interpreted as commands)
    value = re.sub(r'^@', '\\@', value, flags=re.MULTILINE)
    return value


def generate_batch_script(project, username="unknown"):
    """
    Convert project map_data to an Evennia batch command script.

    Args:
        project: BuildProject instance
        username: Builder's username for attribution

    Returns:
        String containing the .ev batch script
    """
    map_data = project.map_data or {}
    rooms = map_data.get("rooms", {})
    exits = map_data.get("exits", {})
    objects = map_data.get("objects", {})

    lines = []
    project_id = project.id

    # Header
    lines.append(f"# Generated by BeckoningMU Web Builder")
    lines.append(f"# Project: {sanitize_string(project.name)}")
    lines.append(f"# Builder: {username}")
    lines.append(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"# Project ID: {project_id}")
    lines.append("#")
    lines.append("# " + "=" * 60)
    lines.append("#")

    # Phase 1: Create sandbox container
    sandbox_alias = f"_sandbox_{project_id}"
    lines.append("# PHASE 1 - Create sandbox container")
    lines.append("#")
    lines.append(f"@dig Builder Sandbox: {sanitize_string(project.name)};{sandbox_alias} : typeclasses.rooms.Room")
    lines.append("#")
    lines.append(f"@tel {sandbox_alias}")
    lines.append("#")

    # Phase 2: Create all rooms
    lines.append("# " + "-" * 60)
    lines.append("# PHASE 2 - Create all rooms")
    lines.append("#")

    for room_id, room in rooms.items():
        room_alias = f"_bld_{project_id}_{room_id}"
        room_name = sanitize_string(room.get("name", "Unnamed Room"))

        lines.append(f"# Room: {room_name}")
        lines.append("#")
        lines.append(f"@dig {room_name};{room_alias} : typeclasses.rooms.Room")
        lines.append("#")

        # Description
        desc = sanitize_string(room.get("description", ""))
        if desc:
            lines.append(f"@desc {room_alias} = {desc}")
            lines.append("#")

        # V5 attributes
        v5 = room.get("v5", {})
        if v5.get("location_type"):
            lines.append(f"@set {room_alias}/location_type = {v5['location_type']}")
            lines.append("#")
        if v5.get("day_night"):
            lines.append(f"@set {room_alias}/day_night = {v5['day_night']}")
            lines.append("#")
        if v5.get("danger_level"):
            lines.append(f"@set {room_alias}/danger_level = {v5['danger_level']}")
            lines.append("#")
        if v5.get("hunting_modifier"):
            lines.append(f"@set {room_alias}/hunting_modifier = {v5['hunting_modifier']}")
            lines.append("#")
        if v5.get("territory_owner"):
            lines.append(f"@set {room_alias}/territory_owner = {v5['territory_owner']}")
            lines.append("#")

        # Haven ratings
        haven = v5.get("haven_ratings", {})
        if haven and v5.get("location_type") == "haven":
            lines.append(f"@set {room_alias}/haven_security = {haven.get('security', 0)}")
            lines.append("#")
            lines.append(f"@set {room_alias}/haven_size = {haven.get('size', 0)}")
            lines.append("#")
            lines.append(f"@set {room_alias}/haven_luxury = {haven.get('luxury', 0)}")
            lines.append("#")
            lines.append(f"@set {room_alias}/haven_warding = {haven.get('warding', 0)}")
            lines.append("#")
            if haven.get("location_hidden"):
                lines.append(f"@set {room_alias}/haven_hidden = True")
                lines.append("#")

        # Triggers (stored as JSON attribute)
        triggers = room.get("triggers", [])
        if triggers:
            import json
            triggers_json = json.dumps(triggers)
            lines.append(f"@set {room_alias}/triggers = {triggers_json}")
            lines.append("#")

        # Tag for tracking
        lines.append(f"@tag {room_alias} = web_builder")
        lines.append("#")
        lines.append(f"@tag {room_alias} = project_{project_id}")
        lines.append("#")

    # Phase 3: Create exits
    lines.append("# " + "-" * 60)
    lines.append("# PHASE 3 - Create exits")
    lines.append("#")

    for exit_id, exit_data in exits.items():
        source_alias = f"_bld_{project_id}_{exit_data['source']}"
        target_alias = f"_bld_{project_id}_{exit_data['target']}"
        exit_name = sanitize_string(exit_data.get("name", "exit"))
        aliases = exit_data.get("aliases", [])

        # Build exit name with aliases
        if aliases:
            exit_full = f"{exit_name};{';'.join(aliases)}"
        else:
            exit_full = exit_name

        lines.append(f"# Exit: {exit_name} ({source_alias} -> {target_alias})")
        lines.append("#")
        lines.append(f"@tel {source_alias}")
        lines.append("#")
        lines.append(f"@open {exit_full} = {target_alias}")
        lines.append("#")

        # Exit description
        exit_desc = sanitize_string(exit_data.get("description", ""))
        if exit_desc:
            lines.append(f"@desc {exit_name} = {exit_desc}")
            lines.append("#")

        # Exit locks
        locks = exit_data.get("locks", "")
        if locks:
            lines.append(f"@lock {exit_name} = {locks}")
            lines.append("#")

    # Phase 4: Create objects
    if objects:
        lines.append("# " + "-" * 60)
        lines.append("# PHASE 4 - Create objects")
        lines.append("#")

        for obj_id, obj_data in objects.items():
            room_alias = f"_bld_{project_id}_{obj_data['room']}"
            obj_name = sanitize_string(obj_data.get("name", "object"))

            lines.append(f"# Object: {obj_name} in {room_alias}")
            lines.append("#")
            lines.append(f"@tel {room_alias}")
            lines.append("#")

            prototype = obj_data.get("prototype")
            if prototype:
                lines.append(f"@spawn {prototype}")
                lines.append("#")
                # Rename if different from prototype
                if obj_name:
                    lines.append(f"@name {prototype.lower()} = {obj_name}")
                    lines.append("#")
            else:
                typeclass = obj_data.get("typeclass", "typeclasses.objects.Object")
                lines.append(f"@create/drop {obj_name} : {typeclass}")
                lines.append("#")

            # Object description
            obj_desc = sanitize_string(obj_data.get("description", ""))
            if obj_desc:
                lines.append(f"@desc {obj_name} = {obj_desc}")
                lines.append("#")

            # Custom attributes
            custom_attrs = obj_data.get("custom_attrs", {})
            for attr_name, attr_value in custom_attrs.items():
                lines.append(f"@set {obj_name}/{attr_name} = {attr_value}")
                lines.append("#")

    # Footer
    lines.append("# " + "=" * 60)
    lines.append("# BUILD COMPLETE")
    lines.append("#")
    lines.append(f"@tel {sandbox_alias}")
    lines.append("#")
    lines.append(f"@py from evennia import logger; logger.log_info('Web Builder: Project {project_id} ({project.name}) built successfully')")
    lines.append("#")

    return "\n".join(lines)
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/exporter.py
git commit -m "feat(builder): add batch script exporter"
```

---

### Task 5.2: Implement Export View

**Files:**
- Modify: `beckonmu/web/builder/views.py`

**Step 1: Add import at top of file**

```python
from .exporter import generate_batch_script
```

**Step 2: Update ExportProjectView**

```python
class ExportProjectView(StaffRequiredMixin, View):
    """Download project as .ev batch file."""

    def get(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Check visibility
        if not project.is_public and project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"},
                status=403
            )

        # Generate script
        script_content = generate_batch_script(project, request.user.username)

        # Return as downloadable file
        filename = f"{project.name.replace(' ', '_')}_build.ev"
        response = HttpResponse(script_content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
```

**Step 3: Commit**

```bash
git add beckonmu/web/builder/views.py
git commit -m "feat(builder): implement export view"
```

---

## Phase 6: Build to Sandbox

### Task 6.1: Create Builder Commands

**Files:**
- Create: `beckonmu/commands/builder.py`

**Step 1: Create the commands file**

```python
"""
Builder commands for promoting and abandoning sandbox builds.
"""
from evennia.commands.command import Command
from evennia.utils.search import search_object
from django.utils import timezone


class CmdPromote(Command):
    """
    Promote a sandbox build to a live location.

    Usage:
        @promote <sandbox_dbref> = <destination>

    This moves all rooms from a builder sandbox to the specified
    destination container room.
    """
    key = "@promote"
    locks = "cmd:perm(Builder) or perm(Admin)"
    help_category = "Building"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: @promote <sandbox_dbref> = <destination>")
            return

        sandbox_ref, dest_ref = self.args.split("=", 1)
        sandbox_ref = sandbox_ref.strip()
        dest_ref = dest_ref.strip()

        # Find sandbox
        sandbox = search_object(sandbox_ref)
        if not sandbox:
            self.caller.msg(f"Could not find sandbox: {sandbox_ref}")
            return
        sandbox = sandbox[0]

        # Verify it's a sandbox
        if not sandbox.tags.has("web_builder"):
            self.caller.msg("That doesn't appear to be a builder sandbox.")
            return

        # Find destination
        dest = search_object(dest_ref)
        if not dest:
            self.caller.msg(f"Could not find destination: {dest_ref}")
            return
        dest = dest[0]

        # Move all contents
        moved_count = 0
        for obj in sandbox.contents:
            obj.move_to(dest, quiet=True)
            moved_count += 1

        # Delete empty sandbox
        sandbox_name = sandbox.key
        sandbox.delete()

        self.caller.msg(f"Promoted {moved_count} objects from '{sandbox_name}' to '{dest.key}'.")

        # Try to update Django project record
        try:
            from beckonmu.web.builder.models import BuildProject
            # Find project by sandbox tag
            project_tag = [t for t in sandbox.tags.all() if t.startswith("project_")]
            if project_tag:
                project_id = int(project_tag[0].replace("project_", ""))
                project = BuildProject.objects.get(pk=project_id)
                project.sandbox_room_id = None
                project.promoted_at = timezone.now()
                project.save()
        except Exception:
            pass  # Non-critical


class CmdAbandon(Command):
    """
    Abandon and delete a sandbox build.

    Usage:
        @abandon <sandbox_dbref>

    This deletes the sandbox and all rooms inside it.
    """
    key = "@abandon"
    locks = "cmd:perm(Builder) or perm(Admin)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: @abandon <sandbox_dbref>")
            return

        sandbox_ref = self.args.strip()

        # Find sandbox
        sandbox = search_object(sandbox_ref)
        if not sandbox:
            self.caller.msg(f"Could not find sandbox: {sandbox_ref}")
            return
        sandbox = sandbox[0]

        # Verify it's a sandbox
        if not sandbox.tags.has("web_builder"):
            self.caller.msg("That doesn't appear to be a builder sandbox.")
            return

        # Confirm
        sandbox_name = sandbox.key
        content_count = len(sandbox.contents)

        # Delete all contents recursively
        def delete_recursive(obj):
            for child in obj.contents:
                delete_recursive(child)
            obj.delete()

        for obj in list(sandbox.contents):
            delete_recursive(obj)

        sandbox.delete()

        self.caller.msg(f"Abandoned sandbox '{sandbox_name}' and deleted {content_count} objects.")

        # Try to update Django project record
        try:
            from beckonmu.web.builder.models import BuildProject
            project_tag = [t for t in sandbox.tags.all() if t.startswith("project_")]
            if project_tag:
                project_id = int(project_tag[0].replace("project_", ""))
                project = BuildProject.objects.get(pk=project_id)
                project.sandbox_room_id = None
                project.save()
        except Exception:
            pass  # Non-critical
```

**Step 2: Commit**

```bash
git add beckonmu/commands/builder.py
git commit -m "feat(builder): add @promote and @abandon commands"
```

---

### Task 6.2: Register Builder Commands

**Files:**
- Modify: `beckonmu/commands/default_cmdsets.py`

**Step 1: Add import and commands to CharacterCmdSet**

Add import at top:
```python
from beckonmu.commands.builder import CmdPromote, CmdAbandon
```

Add to `CharacterCmdSet.at_cmdset_creation()`:
```python
self.add(CmdPromote())
self.add(CmdAbandon())
```

**Step 2: Commit**

```bash
git add beckonmu/commands/default_cmdsets.py
git commit -m "feat(builder): register @promote and @abandon commands"
```

---

### Task 6.3: Implement Build API

**Files:**
- Modify: `beckonmu/web/builder/views.py`

**Step 1: Update BuildProjectView**

```python
@method_decorator(csrf_exempt, name="dispatch")
class BuildProjectView(StaffRequiredMixin, View):
    """Build project to sandbox."""

    def post(self, request, pk, *args, **kwargs):
        project = get_object_or_404(BuildProject, pk=pk)

        # Check ownership
        if project.user != request.user:
            return JsonResponse(
                {"status": "error", "error": "Not authorized"},
                status=403
            )

        # Check if sandbox already exists
        if project.sandbox_room_id:
            return JsonResponse({
                "status": "error",
                "error": "Sandbox already exists. Use @abandon in-game first.",
                "sandbox_id": project.sandbox_room_id
            }, status=400)

        # Generate and execute batch script
        from .exporter import generate_batch_script
        script_content = generate_batch_script(project, request.user.username)

        try:
            # Save script to temp file and execute
            import tempfile
            import os
            from evennia.utils.batchprocessors import BATCHCMD

            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ev', delete=False) as f:
                f.write(script_content)
                temp_path = f.name

            try:
                # Execute batch commands
                # Note: This requires the caller to have appropriate permissions
                from evennia import SESSION_HANDLER
                from evennia.utils import create

                # For now, return the script for manual execution
                # Full automatic execution requires more integration work
                return JsonResponse({
                    "status": "manual_required",
                    "message": "Automatic execution not yet implemented. Download and run manually.",
                    "download_url": f"/builder/export/{pk}/"
                })

            finally:
                # Cleanup temp file
                os.unlink(temp_path)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "error": str(e)
            }, status=500)
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/views.py
git commit -m "feat(builder): implement build API (manual execution)"
```

---

## Phase 7: Validation and Testing

### Task 7.1: Create Validators

**Files:**
- Create: `beckonmu/web/builder/validators.py`

**Step 1: Create validators**

```python
"""
Validation utilities for the Web Builder.
"""


def validate_project(map_data):
    """
    Validate a project's map data before building.

    Returns:
        tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    rooms = map_data.get("rooms", {})
    exits = map_data.get("exits", {})

    if not rooms:
        errors.append("Project has no rooms.")
        return False, errors, warnings

    # Check for isolated rooms (no exits)
    room_connections = {rid: {"in": [], "out": []} for rid in rooms}

    for exit_id, exit_data in exits.items():
        source = exit_data.get("source")
        target = exit_data.get("target")

        if source not in rooms:
            errors.append(f"Exit '{exit_id}' has invalid source room '{source}'")
        else:
            room_connections[source]["out"].append(exit_id)

        if target not in rooms:
            errors.append(f"Exit '{exit_id}' has invalid target room '{target}'")
        else:
            room_connections[target]["in"].append(exit_id)

    # Warn about isolated rooms
    for room_id, connections in room_connections.items():
        room_name = rooms[room_id].get("name", room_id)
        if not connections["in"] and not connections["out"]:
            warnings.append(f"Room '{room_name}' has no exits (isolated)")
        elif not connections["in"] and len(rooms) > 1:
            warnings.append(f"Room '{room_name}' has no incoming exits (unreachable)")

    # Warn about empty descriptions
    for room_id, room in rooms.items():
        if not room.get("description"):
            warnings.append(f"Room '{room.get('name', room_id)}' has no description")

    # Check for duplicate room names
    names = [r.get("name", "") for r in rooms.values()]
    duplicates = set(n for n in names if names.count(n) > 1 and n)
    for name in duplicates:
        warnings.append(f"Multiple rooms named '{name}'")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/validators.py
git commit -m "feat(builder): add project validators"
```

---

### Task 7.2: Add Validation to Save API

**Files:**
- Modify: `beckonmu/web/builder/views.py`

**Step 1: Update SaveProjectView to include validation**

Add import:
```python
from .validators import validate_project
```

Update the save response to include validation:
```python
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

        # Validate
        is_valid, errors, warnings = validate_project(map_data)

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

        return JsonResponse({
            "status": "success",
            "id": project.id,
            "validation": {
                "is_valid": is_valid,
                "errors": errors,
                "warnings": warnings
            }
        })
```

**Step 2: Commit**

```bash
git add beckonmu/web/builder/views.py
git commit -m "feat(builder): add validation to save API"
```

---

## Phase 8: Final Integration

### Task 8.1: Verify Server Reload

**Step 1: Reload Evennia**

```bash
cd C:\Users\dasbl\PycharmProjects\TheBeckoningMU
evennia reload
```

Expected: Server reloads without errors

**Step 2: Verify migrations**

```bash
evennia migrate --check
```

Expected: "No migrations to apply" or successful application

**Step 3: Test URL access**

Start server if not running:
```bash
evennia start
```

Open browser to: `http://localhost:4001/builder/`

Expected: Dashboard page loads (may require staff login)

---

### Task 8.2: Final Commit

**Step 1: Create final commit**

```bash
git add -A
git commit -m "feat(builder): complete Web Builder Phase 1 implementation

Implemented:
- Django app with BuildProject and RoomTemplate models
- Dashboard and Editor views
- Grid-based room placement with drag-and-drop
- Exit creation between rooms
- V5 location attributes (type, day/night, danger, hunting)
- Haven ratings for haven rooms
- Batch script exporter (.ev format)
- Project save/load API
- Export to downloadable .ev file
- @promote and @abandon commands
- Project validation

Remaining for Phase 2:
- Compass mode for quick room creation
- Object/item placement
- Trigger system UI
- Automatic build execution
- Room templates
"
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] `evennia reload` completes without errors
- [ ] `/builder/` loads dashboard page
- [ ] Can create new project
- [ ] Can add rooms to grid
- [ ] Can drag rooms to reposition
- [ ] Can create exits between rooms
- [ ] Can edit room properties (name, description, V5 settings)
- [ ] Can save project
- [ ] Can export .ev file
- [ ] Exported .ev file has correct syntax
- [ ] `@promote` command is available to staff
- [ ] `@abandon` command is available to staff

---

## File Summary

**New Files Created:**
- `beckonmu/world/v5_locations.py`
- `beckonmu/web/builder/__init__.py`
- `beckonmu/web/builder/apps.py`
- `beckonmu/web/builder/models.py`
- `beckonmu/web/builder/admin.py`
- `beckonmu/web/builder/urls.py`
- `beckonmu/web/builder/views.py`
- `beckonmu/web/builder/exporter.py`
- `beckonmu/web/builder/validators.py`
- `beckonmu/web/builder/migrations/__init__.py`
- `beckonmu/web/builder/migrations/0001_initial.py`
- `beckonmu/web/templates/builder/dashboard.html`
- `beckonmu/web/templates/builder/editor.html`
- `beckonmu/commands/builder.py`

**Modified Files:**
- `beckonmu/server/conf/settings.py` (add app to INSTALLED_APPS)
- `beckonmu/web/urls.py` (add builder URL include)
- `beckonmu/commands/default_cmdsets.py` (register builder commands)
