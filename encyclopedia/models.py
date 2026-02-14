from django.db import models
from django.conf import settings


class Entry(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("under_review", "Under Review"),
        ("verified", "Verified"),
        ("disputed", "Disputed"),
    ]

    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wiki_entries",
    )
    is_locked = models.BooleanField(default=False)
    lock_reason = models.CharField(max_length=255, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locked_wiki_entries",
    )
    locked_at = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, default="draft"
    )
    verification_note = models.CharField(max_length=255, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_wiki_entries",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class EntryRevision(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="revisions")
    content = models.TextField()
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entry_revisions",
    )
    edit_summary = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.entry.title} revision at {self.created_at}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("edit", "Edit"),
        ("delete", "Delete"),
        ("lock", "Lock"),
        ("unlock", "Unlock"),
        ("rollback", "Rollback"),
        ("verify", "Verify"),
        ("dispute_reported", "Dispute Reported"),
        ("dispute_resolved", "Dispute Resolved"),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entry_title = models.CharField(max_length=200)
    entry = models.ForeignKey(
        Entry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wiki_audit_logs",
    )
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.entry_title}"


class Dispute(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="disputes")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_disputes",
    )
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_disputes",
    )
    resolution_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dispute on {self.entry.title} ({self.status})"
