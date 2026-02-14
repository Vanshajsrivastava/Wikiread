from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import AuditLog, Dispute, Entry, EntryRevision


class EncyclopediaViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator", password="pass1234")
        self.other_user = User.objects.create_user(username="other", password="pass1234")
        self.staff_user = User.objects.create_user(
            username="staff", password="pass1234", is_staff=True
        )
        self.super_user = User.objects.create_superuser(
            username="super", password="pass1234", email="super@example.com"
        )
        Entry.objects.create(
            title="Python",
            content="# Python\nA language",
            created_by=self.creator,
        )
        Entry.objects.create(title="Django", content="# Django\nA framework")

    def test_index_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")

    def test_entry_loads_case_insensitive(self):
        response = self.client.get(reverse("entry", kwargs={"title": "python"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")

    def test_search_exact_redirects_to_entry(self):
        response = self.client.get(reverse("search"), {"q": "python"})
        self.assertEqual(response.status_code, 302)

    def test_search_partial_shows_results(self):
        response = self.client.get(reverse("search"), {"q": "dj"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

    def test_search_matches_content(self):
        response = self.client.get(reverse("search"), {"q": "framework"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

    def test_create_new_entry(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(
            reverse("new_page"),
            {"title": "Flask", "content": "# Flask"},
        )
        self.assertEqual(response.status_code, 302)
        new_entry = Entry.objects.get(title="Flask")
        self.assertEqual(new_entry.created_by, self.creator)

    def test_edit_entry(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(
            reverse("save_edit", kwargs={"title": "Python"}),
            {"content": "# Python\nUpdated"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("Updated", Entry.objects.get(title="Python").content)

    def test_new_page_requires_login(self):
        response = self.client.get(reverse("new_page"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_edit_requires_login(self):
        response = self.client.get(reverse("edit", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_save_edit_requires_login(self):
        response = self.client.post(
            reverse("save_edit", kwargs={"title": "Python"}),
            {"content": "Blocked"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_preview_markdown_returns_html(self):
        response = self.client.get(reverse("preview_markdown"), {"text": "# Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("<h1>Hello</h1>", response.json()["html"])

    def test_delete_entry(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(reverse("delete_entry", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Entry.objects.filter(title="Python").exists())

    def test_delete_entry_requires_post(self):
        response = self.client.get(reverse("delete_entry", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Entry.objects.filter(title="Python").exists())

    def test_delete_entry_forbidden_for_non_owner(self):
        self.client.login(username="other", password="pass1234")
        response = self.client.post(reverse("delete_entry", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Entry.objects.filter(title="Python").exists())

    def test_delete_entry_forbidden_for_staff_non_superuser(self):
        self.client.login(username="staff", password="pass1234")
        response = self.client.post(reverse("delete_entry", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Entry.objects.filter(title="Python").exists())

    def test_delete_entry_allowed_for_superuser(self):
        self.client.login(username="super", password="pass1234")
        response = self.client.post(reverse("delete_entry", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Entry.objects.filter(title="Python").exists())

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_dashboard_for_normal_user(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Dashboard")

    def test_dashboard_for_superuser(self):
        self.client.login(username="super", password="pass1234")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Dashboard")

    def test_register_creates_account_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "NewStrongPass123",
                "password2": "NewStrongPass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_login_flow(self):
        response = self.client.post(
            reverse("login"),
            {"username": "creator", "password": "pass1234"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_edit_creates_revision_and_audit_log(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(
            reverse("save_edit", kwargs={"title": "Python"}),
            {"content": "# Python\nChanged", "edit_summary": "Updated intro"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EntryRevision.objects.filter(entry__title="Python").exists())
        self.assertTrue(AuditLog.objects.filter(action="edit", entry_title="Python").exists())

    def test_superuser_can_lock_and_unlock_page(self):
        self.client.login(username="super", password="pass1234")
        lock_response = self.client.post(
            reverse("toggle_lock", kwargs={"title": "Python"}),
            {"lock_reason": "Policy freeze"},
        )
        self.assertEqual(lock_response.status_code, 302)
        self.assertTrue(Entry.objects.get(title="Python").is_locked)

        unlock_response = self.client.post(reverse("toggle_lock", kwargs={"title": "Python"}))
        self.assertEqual(unlock_response.status_code, 302)
        self.assertFalse(Entry.objects.get(title="Python").is_locked)

    def test_non_superuser_cannot_lock_page(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(reverse("toggle_lock", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 403)

    def test_locked_page_blocks_non_superuser_edit(self):
        entry = Entry.objects.get(title="Python")
        entry.is_locked = True
        entry.save(update_fields=["is_locked"])

        self.client.login(username="creator", password="pass1234")
        response = self.client.get(reverse("edit", kwargs={"title": "Python"}))
        self.assertEqual(response.status_code, 423)

    def test_rollback_revision(self):
        self.client.login(username="creator", password="pass1234")
        EntryRevision.objects.create(
            entry=Entry.objects.get(title="Python"),
            content="# Python\nOld",
            edited_by=self.creator,
            edit_summary="Old snapshot",
        )
        revision = EntryRevision.objects.filter(entry__title="Python").first()

        response = self.client.post(
            reverse("rollback_revision", kwargs={"title": "Python", "revision_id": revision.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("Old", Entry.objects.get(title="Python").content)
        self.assertTrue(AuditLog.objects.filter(action="rollback", entry_title="Python").exists())

    def test_audit_logs_access_superuser_only(self):
        self.client.login(username="creator", password="pass1234")
        forbidden = self.client.get(reverse("audit_logs"))
        self.assertEqual(forbidden.status_code, 403)

        self.client.login(username="super", password="pass1234")
        allowed = self.client.get(reverse("audit_logs"))
        self.assertEqual(allowed.status_code, 200)

    def test_report_dispute_marks_entry_disputed(self):
        self.client.login(username="other", password="pass1234")
        response = self.client.post(
            reverse("report_dispute", kwargs={"title": "Python"}),
            {"message": "This claim has no source."},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Dispute.objects.filter(entry__title="Python", status="open").count(), 1)
        self.assertEqual(Entry.objects.get(title="Python").verification_status, "disputed")

    def test_report_dispute_requires_login(self):
        response = self.client.post(
            reverse("report_dispute", kwargs={"title": "Python"}),
            {"message": "Guest report"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_superuser_can_update_verification_status(self):
        self.client.login(username="super", password="pass1234")
        response = self.client.post(
            reverse("set_verification_status", kwargs={"title": "Python"}),
            {"verification_status": "verified", "verification_note": "Checked with sources"},
        )
        self.assertEqual(response.status_code, 302)
        entry = Entry.objects.get(title="Python")
        self.assertEqual(entry.verification_status, "verified")
        self.assertEqual(entry.verified_by, self.super_user)

    def test_non_superuser_cannot_update_verification_status(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(
            reverse("set_verification_status", kwargs={"title": "Python"}),
            {"verification_status": "verified"},
        )
        self.assertEqual(response.status_code, 403)

    def test_disputes_queue_superuser_only(self):
        self.client.login(username="creator", password="pass1234")
        forbidden = self.client.get(reverse("disputes_queue"))
        self.assertEqual(forbidden.status_code, 403)

        self.client.login(username="super", password="pass1234")
        allowed = self.client.get(reverse("disputes_queue"))
        self.assertEqual(allowed.status_code, 200)

    def test_superuser_resolves_dispute(self):
        dispute = Dispute.objects.create(
            entry=Entry.objects.get(title="Python"),
            reported_by=self.other_user,
            message="Possible error",
            status="open",
        )
        self.client.login(username="super", password="pass1234")
        response = self.client.post(
            reverse("resolve_dispute", kwargs={"dispute_id": dispute.id}),
            {"resolution": "resolved", "resolution_note": "Claim updated"},
        )
        self.assertEqual(response.status_code, 302)
        dispute.refresh_from_db()
        self.assertEqual(dispute.status, "resolved")
        self.assertTrue(AuditLog.objects.filter(action="dispute_resolved").exists())
