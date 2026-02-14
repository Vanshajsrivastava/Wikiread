from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("audit-logs/", views.audit_logs, name="audit_logs"),
    path("disputes/", views.disputes_queue, name="disputes_queue"),
    path("disputes/<int:dispute_id>/resolve/", views.resolve_dispute, name="resolve_dispute"),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("preview/", views.preview_markdown, name="preview_markdown"),
    path("search/", views.search, name="search"),
    path("new/", views.new_page, name="new_page"),
    path("random/", views.rand, name="rand"),
    path("edit/<str:title>/", views.edit, name="edit"),
    path("edit/<str:title>/save/", views.save_edit, name="save_edit"),
    path("delete/<str:title>/", views.delete_entry, name="delete_entry"),
    path("wiki/<str:title>/revisions/", views.revisions, name="revisions"),
    path(
        "wiki/<str:title>/rollback/<int:revision_id>/",
        views.rollback_revision,
        name="rollback_revision",
    ),
    path("wiki/<str:title>/lock/", views.toggle_lock, name="toggle_lock"),
    path("wiki/<str:title>/verify/", views.set_verification_status, name="set_verification_status"),
    path("wiki/<str:title>/dispute/", views.report_dispute, name="report_dispute"),
    path("wiki/<str:title>/", views.entry, name="entry"),
]
