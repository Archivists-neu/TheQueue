def GetApiRoute(routLink: str) -> str:
    return f"http://web-api:4000/{routLink}"

def GetUsersApi() -> str:
    return GetApiRoute("user/users")


