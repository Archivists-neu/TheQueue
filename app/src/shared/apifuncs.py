def GetApiRoute(routLink: str) -> str:
    return f"http://web-api:4000/{routLink}"

def GetUsersApi() -> str:
    return GetApiRoute("user/users")

def GetMediaApi() -> str:
    return GetApiRoute("media")

def GetMediaSearchApi() -> str:
    return GetApiRoute("media/search")

