import random

import markdown
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse

from . import util
from .models import AuditLog, Dispute, Entry, EntryRevision


def _can_delete_entry(request, entry_obj):
    user = request.user
    return user.is_authenticated and (user.is_superuser or entry_obj.created_by_id == user.id)


def _can_moderate(request):
    return request.user.is_authenticated and request.user.is_superuser


def _can_rollback(request, entry_obj):
    return request.user.is_authenticated and (
        request.user.is_superuser or entry_obj.created_by_id == request.user.id
    )


def _log_action(action, entry, actor, details=""):
    AuditLog.objects.create(
        action=action,
        entry=entry,
        entry_title=entry.title,
        actor=actor if actor and actor.is_authenticated else None,
        details=details,
    )


@login_required
def dashboard(request):
    user = request.user
    your_entries = Entry.objects.filter(created_by=user).order_by("-updated_at")

    context = {
        "is_admin_dashboard": user.is_superuser,
        "total_entries": Entry.objects.count(),
        "locked_entries_count": Entry.objects.filter(is_locked=True).count(),
        "verified_entries_count": Entry.objects.filter(verification_status="verified").count(),
        "revision_count": EntryRevision.objects.count(),
        "pending_disputes_count": Dispute.objects.filter(status="open").count(),
        "your_entries_count": your_entries.count(),
        "your_recent_entries": your_entries[:8],
        "your_recent_activity": AuditLog.objects.filter(actor=user)[:10],
    }

    if user.is_superuser:
        context["all_recent_entries"] = Entry.objects.select_related("created_by").order_by(
            "-updated_at"
        )[:12]
        context["recent_audit_logs"] = AuditLog.objects.select_related("actor")[:20]
        context["pending_disputes"] = Dispute.objects.select_related(
            "entry", "reported_by"
        ).filter(status="open")[:15]

    return render(request, "encyclopedia/dashboard.html", context)


@login_required
def audit_logs(request):
    if not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Only superusers can access audit logs."},
            status=403,
        )

    logs = AuditLog.objects.select_related("actor")[:100]
    return render(request, "encyclopedia/audit_logs.html", {"logs": logs})


@login_required
def disputes_queue(request):
    if not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Only superusers can access dispute queue."},
            status=403,
        )

    disputes = Dispute.objects.select_related("entry", "reported_by", "resolved_by")[:200]
    return render(request, "encyclopedia/disputes_queue.html", {"disputes": disputes})


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse("dashboard"))

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))
    else:
        form = UserCreationForm()

    return render(request, "encyclopedia/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("dashboard"))

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse("dashboard"))
    else:
        form = AuthenticationForm(request)

    return render(request, "encyclopedia/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect(reverse("index"))
    return redirect(reverse("dashboard"))


def convert_md_to_html(title):
    content = util.get_entry(title)
    markdowner = markdown.Markdown()
    if content is None:
        return None
    return markdowner.convert(content)


def index(request):
    entries = util.list_entries()
    return render(
        request,
        "encyclopedia/index.html",
        {
            "entries": entries,
            "recent_entries": entries[:5],
            "locked_entries": Entry.objects.filter(is_locked=True).count(),
        },
    )


def entry(request, title):
    entry_obj = util.get_entry_obj(title)
    if entry_obj is None:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "This entry does not exist.",
            },
            status=404,
        )

    html_content = convert_md_to_html(entry_obj.title)
    return render(
        request,
        "encyclopedia/entry.html",
        {
            "title": entry_obj.title,
            "content": html_content,
            "can_delete": _can_delete_entry(request, entry_obj),
            "can_moderate": _can_moderate(request),
            "can_rollback": _can_rollback(request, entry_obj),
            "entry_owner": entry_obj.created_by.username if entry_obj.created_by else "Unknown",
            "is_locked": entry_obj.is_locked,
            "lock_reason": entry_obj.lock_reason,
            "locked_by": entry_obj.locked_by.username if entry_obj.locked_by else "Unknown",
            "verification_status": entry_obj.verification_status,
            "verification_status_label": entry_obj.get_verification_status_display(),
            "verification_note": entry_obj.verification_note,
            "verified_by": entry_obj.verified_by.username if entry_obj.verified_by else "Unknown",
            "open_disputes_count": entry_obj.disputes.filter(status="open").count(),
        },
    )


def search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return render(
            request,
            "encyclopedia/search.html",
            {
                "query": query,
                "recommendation": [],
            },
        )

    exact_match = util.get_entry_obj(query)
    if exact_match is not None:
        return redirect(reverse("entry", kwargs={"title": exact_match.title}))

    recommendations = util.search_entries(query)
    return render(
        request,
        "encyclopedia/search.html",
        {
            "query": query,
            "recommendation": recommendations,
        },
    )


@login_required
def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new.html")

    title = request.POST.get("title", "").strip()
    content = request.POST.get("content", "").strip()

    if not title or not content:
        return render(
            request,
            "encyclopedia/new.html",
            {
                "message": "Both title and content are required.",
                "title": title,
                "content": content,
            },
            status=400,
        )

    if util.get_entry_obj(title) is not None:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "Entry page already exists.",
            },
            status=409,
        )

    saved = util.save_entry(title, content, creator=request.user)
    _log_action("create", saved, request.user, "Created new entry")
    return redirect(reverse("entry", kwargs={"title": saved.title}))


@login_required
def edit(request, title):
    entry_obj = util.get_entry_obj(title)
    if entry_obj is None:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "Cannot edit a page that does not exist.",
            },
            status=404,
        )

    if entry_obj.is_locked and not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "This page is locked by moderation and cannot be edited right now."},
            status=423,
        )

    return render(
        request,
        "encyclopedia/edit.html",
        {
            "title": entry_obj.title,
            "content": entry_obj.content,
        },
    )


@login_required
def save_edit(request, title):
    if request.method != "POST":
        return redirect(reverse("edit", kwargs={"title": title}))

    entry_obj = util.get_entry_obj(title)
    if entry_obj is None:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "Cannot save changes for a page that does not exist.",
            },
            status=404,
        )

    if entry_obj.is_locked and not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "This page is locked by moderation and cannot be edited right now."},
            status=423,
        )

    content = request.POST.get("content", "").strip()
    summary = request.POST.get("edit_summary", "").strip()
    if not content:
        return render(
            request,
            "encyclopedia/edit.html",
            {
                "title": entry_obj.title,
                "content": entry_obj.content,
                "message": "Content cannot be empty.",
            },
            status=400,
        )

    if content != entry_obj.content:
        EntryRevision.objects.create(
            entry=entry_obj,
            content=entry_obj.content,
            edited_by=request.user,
            edit_summary=summary or "Edit snapshot",
        )

    util.save_entry(entry_obj.title, content)
    _log_action("edit", entry_obj, request.user, summary or "Updated entry content")
    return redirect(reverse("entry", kwargs={"title": entry_obj.title}))


@login_required
def revisions(request, title):
    entry_obj = get_object_or_404(Entry, title__iexact=title)
    return render(
        request,
        "encyclopedia/revisions.html",
        {
            "entry": entry_obj,
            "revisions": entry_obj.revisions.select_related("edited_by"),
            "can_rollback": _can_rollback(request, entry_obj),
        },
    )


@login_required
def rollback_revision(request, title, revision_id):
    if request.method != "POST":
        return redirect(reverse("revisions", kwargs={"title": title}))

    entry_obj = get_object_or_404(Entry, title__iexact=title)
    if not _can_rollback(request, entry_obj):
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Only the page creator or a superuser can rollback revisions."},
            status=403,
        )

    revision = get_object_or_404(EntryRevision, id=revision_id, entry=entry_obj)

    EntryRevision.objects.create(
        entry=entry_obj,
        content=entry_obj.content,
        edited_by=request.user,
        edit_summary="Pre-rollback snapshot",
    )

    entry_obj.content = revision.content
    entry_obj.save(update_fields=["content", "updated_at"])
    _log_action("rollback", entry_obj, request.user, f"Rolled back to revision {revision.id}")
    return redirect(reverse("entry", kwargs={"title": entry_obj.title}))


@login_required
def toggle_lock(request, title):
    if request.method != "POST":
        return redirect(reverse("entry", kwargs={"title": title}))

    entry_obj = get_object_or_404(Entry, title__iexact=title)
    if not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Only superusers can lock or unlock pages."},
            status=403,
        )

    if entry_obj.is_locked:
        entry_obj.is_locked = False
        entry_obj.lock_reason = ""
        entry_obj.locked_by = None
        entry_obj.locked_at = None
        entry_obj.save(update_fields=["is_locked", "lock_reason", "locked_by", "locked_at"])
        _log_action("unlock", entry_obj, request.user, "Unlocked entry")
    else:
        reason = request.POST.get("lock_reason", "").strip()
        entry_obj.is_locked = True
        entry_obj.lock_reason = reason
        entry_obj.locked_by = request.user
        entry_obj.locked_at = timezone.now()
        entry_obj.save(update_fields=["is_locked", "lock_reason", "locked_by", "locked_at"])
        _log_action("lock", entry_obj, request.user, reason or "Locked entry")

    return redirect(reverse("entry", kwargs={"title": entry_obj.title}))


@login_required
def set_verification_status(request, title):
    if request.method != "POST":
        return redirect(reverse("entry", kwargs={"title": title}))

    entry_obj = get_object_or_404(Entry, title__iexact=title)
    if not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Only superusers can update verification status."},
            status=403,
        )

    requested_status = request.POST.get("verification_status", "draft")
    note = request.POST.get("verification_note", "").strip()
    allowed = {"draft", "under_review", "verified", "disputed"}
    if requested_status not in allowed:
        requested_status = "draft"

    entry_obj.verification_status = requested_status
    entry_obj.verification_note = note
    if requested_status == "verified":
        entry_obj.verified_by = request.user
        entry_obj.verified_at = timezone.now()
    else:
        entry_obj.verified_by = None
        entry_obj.verified_at = None
    entry_obj.save(
        update_fields=[
            "verification_status",
            "verification_note",
            "verified_by",
            "verified_at",
        ]
    )
    _log_action("verify", entry_obj, request.user, f"Status set to {requested_status}")
    return redirect(reverse("entry", kwargs={"title": entry_obj.title}))


@login_required
def report_dispute(request, title):
    if request.method != "POST":
        return redirect(reverse("entry", kwargs={"title": title}))

    entry_obj = get_object_or_404(Entry, title__iexact=title)
    message = request.POST.get("message", "").strip()
    if not message:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Dispute message cannot be empty."},
            status=400,
        )

    Dispute.objects.create(entry=entry_obj, reported_by=request.user, message=message, status="open")
    if entry_obj.verification_status != "disputed":
        entry_obj.verification_status = "disputed"
        entry_obj.save(update_fields=["verification_status"])
    _log_action("dispute_reported", entry_obj, request.user, "Dispute reported")
    return redirect(reverse("entry", kwargs={"title": entry_obj.title}))


@login_required
def resolve_dispute(request, dispute_id):
    if request.method != "POST":
        return redirect(reverse("disputes_queue"))
    if not request.user.is_superuser:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "Only superusers can resolve disputes."},
            status=403,
        )

    dispute = get_object_or_404(Dispute, id=dispute_id)
    resolution = request.POST.get("resolution", "resolved")
    note = request.POST.get("resolution_note", "").strip()
    if resolution not in {"resolved", "rejected"}:
        resolution = "resolved"

    dispute.status = resolution
    dispute.resolved_by = request.user
    dispute.resolution_note = note
    dispute.resolved_at = timezone.now()
    dispute.save(update_fields=["status", "resolved_by", "resolution_note", "resolved_at"])

    # If all disputes are closed, move page back to review state for follow-up verification.
    if not dispute.entry.disputes.filter(status="open").exists():
        if dispute.entry.verification_status == "disputed":
            dispute.entry.verification_status = "under_review"
            dispute.entry.save(update_fields=["verification_status"])

    _log_action(
        "dispute_resolved",
        dispute.entry,
        request.user,
        f"Dispute {dispute.id} marked {resolution}",
    )
    return redirect(reverse("disputes_queue"))


def rand(request):
    all_entries = util.list_entries()
    if not all_entries:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "No entries available yet.",
            },
            status=404,
        )

    random_entry = random.choice(all_entries)
    return redirect(reverse("entry", kwargs={"title": random_entry}))


def preview_markdown(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET is allowed."}, status=405)

    text = request.GET.get("text", "")
    markdowner = markdown.Markdown()
    html = markdowner.convert(text)
    return JsonResponse({"html": html})


@login_required
def delete_entry(request, title):
    if request.method != "POST":
        return redirect(reverse("entry", kwargs={"title": title}))

    entry_obj = util.get_entry_obj(title)
    if entry_obj is None:
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "Cannot delete a page that does not exist.",
            },
            status=404,
        )

    if not _can_delete_entry(request, entry_obj):
        return render(
            request,
            "encyclopedia/error.html",
            {
                "message": "Only the page creator or a superuser can delete this page.",
            },
            status=403,
        )

    _log_action("delete", entry_obj, request.user, "Deleted entry")
    util.delete_entry(title)
    return redirect(reverse("index"))
