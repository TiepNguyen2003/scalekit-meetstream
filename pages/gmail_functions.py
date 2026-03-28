from __future__ import annotations

try:
    from pages.scalekit_auth import (
        GMAIL_PEOPLE_SCOPE,
        IDENTIFIER,
        ensure_authenticated,
        scalekit,
    )
except ModuleNotFoundError:
    from scalekit_auth import GMAIL_PEOPLE_SCOPE, IDENTIFIER, ensure_authenticated, scalekit


DEFAULT_PERSON_FIELDS = [
    "names",
    "emailAddresses",
    "organizations",
    "phoneNumbers",
]



def gmail_get_people(
    query: str = "John",
    other_contacts: bool = True,
    page_size: int = 10,
    person_fields: list[str] | None = None,
    schema_version: str | None = None,
    tool_version: str | None = None,
):
    if not query or not query.strip():
        raise ValueError("query is required for gmail_get_people")

    ensure_authenticated(required_scopes=[GMAIL_PEOPLE_SCOPE])

    tool_input = {
        "query": query.strip(),
        "other_contacts": other_contacts,
        "page_size": page_size,
        "person_fields": person_fields or DEFAULT_PERSON_FIELDS,
    }

    if schema_version:
        tool_input["schema_version"] = schema_version
    if tool_version:
        tool_input["tool_version"] = tool_version

    result = scalekit.actions.execute_tool(
        tool_name="gmail_search_people",
        identifier=IDENTIFIER,
        tool_input=tool_input,
    )

    return getattr(result, "data", result)


if __name__ == "__main__":
    print(gmail_get_people())
