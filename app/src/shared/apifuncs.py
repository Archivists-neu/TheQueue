from urllib.parse import quote

MEDIA_COLLECTION = "media"


def GetApiRoute(routLink: str) -> str:
    return f"http://web-api:4000/{routLink}"

def GetUsersApi() -> str:
    return GetApiRoute("user")

def GetMediaApi() -> str:
    return GetApiRoute("media")

def GetMediaSearchApi() -> str:
    return GetApiRoute("/search")

def GetMediaSearchApi(**criteria: str) -> str:
    """Pick the narrowest media endpoint that can serve `criteria`.

    The path routes each filter on a single column, so they only apply when
    exactly one criterion was given -- the `**rest` guard enforces that.
    Anything else falls through to the collection route, which ANDs the
    filters together as query params.
    """
    match criteria:
        case {"media_id": media_id, **rest} if not rest:
            return GetApiRoute(f"{MEDIA_COLLECTION}/{media_id}")
        case {"title": title, **rest} if not rest:
            return GetApiRoute(f"{MEDIA_COLLECTION}/title/{quote(title)}")
        case {"media_type": media_type, **rest} if not rest:
            return GetApiRoute(f"{MEDIA_COLLECTION}/type/{quote(media_type)}")
        case _:
            return GetApiRoute(MEDIA_COLLECTION)
