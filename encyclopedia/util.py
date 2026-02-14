from typing import List, Optional

from django.db.models import Q

from .models import Entry


def list_entries() -> List[str]:
    """Returns a sorted list of entry titles."""
    return list(Entry.objects.values_list("title", flat=True))


def save_entry(title: str, content: str, creator=None) -> Entry:
    """Creates or updates an entry by title (case-insensitive)."""
    existing = Entry.objects.filter(title__iexact=title).first()
    if existing:
        existing.content = content
        existing.save(update_fields=["content", "updated_at"])
        return existing

    return Entry.objects.create(title=title, content=content, created_by=creator)


def get_entry(title: str) -> Optional[str]:
    """Returns markdown content for an entry title, or None."""
    entry = Entry.objects.filter(title__iexact=title).first()
    return None if entry is None else entry.content


def get_entry_obj(title: str) -> Optional[Entry]:
    """Returns the entry object for an entry title, or None."""
    return Entry.objects.filter(title__iexact=title).first()


def search_entries(query: str) -> List[Entry]:
    """Returns entries with title or content containing query (case-insensitive)."""
    return list(
        Entry.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        .distinct()
        .order_by("title")
    )


def delete_entry(title: str) -> bool:
    """Deletes an entry by title (case-insensitive). Returns True if deleted."""
    entry = Entry.objects.filter(title__iexact=title).first()
    if entry is None:
        return False
    entry.delete()
    return True
