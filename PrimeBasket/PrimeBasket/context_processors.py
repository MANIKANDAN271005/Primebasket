def auth_status(request):
    return {
        "is_authenticated": bool(request.session.get("user_email")),
        "current_user_fullname": request.session.get("user_fullname", ""),
    }
