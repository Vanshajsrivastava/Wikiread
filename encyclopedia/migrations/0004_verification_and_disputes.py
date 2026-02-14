from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("encyclopedia", "0003_entry_moderation_and_history"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="entry",
            name="verification_note",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="entry",
            name="verification_status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("under_review", "Under Review"),
                    ("verified", "Verified"),
                    ("disputed", "Disputed"),
                ],
                default="draft",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="entry",
            name="verified_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="verified_wiki_entries",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="Dispute",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("resolved", "Resolved"), ("rejected", "Rejected")],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("resolution_note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disputes",
                        to="encyclopedia.entry",
                    ),
                ),
                (
                    "reported_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reported_disputes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resolved_disputes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterField(
            model_name="auditlog",
            name="action",
            field=models.CharField(
                choices=[
                    ("create", "Create"),
                    ("edit", "Edit"),
                    ("delete", "Delete"),
                    ("lock", "Lock"),
                    ("unlock", "Unlock"),
                    ("rollback", "Rollback"),
                    ("verify", "Verify"),
                    ("dispute_reported", "Dispute Reported"),
                    ("dispute_resolved", "Dispute Resolved"),
                ],
                max_length=20,
            ),
        ),
    ]
