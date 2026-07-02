"""
Generic helper utilities.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time."""
    return datetime.now(timezone.utc)


def format_response(success: bool, message: str, data: dict | list | None = None) -> dict:
    """
    Standard JSON response format.

    Args:
        success: Whether the operation was successful.
        message: Human-readable message.
        data: Optional payload data.

    Returns:
        Formatted response dict.
    """
    response = {
        "success": success,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return response


def paginate(items: list, page: int = 1, per_page: int = 20) -> dict:
    """
    Simple list pagination helper.

    Args:
        items: Full list of items.
        page: Current page (1-indexed).
        per_page: Items per page.

    Returns:
        Dict with paginated items and metadata.
    """
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }
