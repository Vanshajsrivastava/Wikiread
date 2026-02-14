from django.contrib import admin

from .models import AuditLog, Dispute, Entry, EntryResource, EntryRevision


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_by",
        "lead_image_url",
        "verification_status",
        "is_locked",
        "updated_at",
        "created_at",
    )
    search_fields = ("title", "content")


@admin.register(EntryRevision)
class EntryRevisionAdmin(admin.ModelAdmin):
    list_display = ("entry", "edited_by", "created_at")
    search_fields = ("entry__title", "edit_summary")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entry_title", "actor", "created_at")
    search_fields = ("entry_title", "details", "actor__username")


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("entry", "status", "reported_by", "resolved_by", "created_at")
    search_fields = ("entry__title", "message", "resolution_note")


@admin.register(EntryResource)
class EntryResourceAdmin(admin.ModelAdmin):
    list_display = ("entry", "resource_type", "label", "added_by", "created_at")
    search_fields = ("entry__title", "label", "url")
