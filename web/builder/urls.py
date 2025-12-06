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
