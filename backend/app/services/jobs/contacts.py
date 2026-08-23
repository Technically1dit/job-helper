import re

EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.IGNORECASE)
RECRUITMENT_TERMS = ("recruit", "talent", "hiring", "career", "human resources", " hr ")


def verified_email_from_source(email: str | None, source_text: str) -> str | None:
    """Return an address only when it occurs verbatim in provider evidence."""
    if not email:
        return None
    found = {item.casefold() for item in EMAIL_RE.findall(source_text or "")}
    return email if email.casefold() in found else None


def recruitment_role_supported(email: str, source_text: str) -> bool:
    for line in (source_text or "").splitlines():
        if email.casefold() in line.casefold() and any(term in line.casefold() for term in RECRUITMENT_TERMS):
            return True
    return False
