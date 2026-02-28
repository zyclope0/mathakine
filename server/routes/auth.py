"""Routes API authentification."""

from starlette.routing import Route

from server.handlers.auth_handlers import (
    api_forgot_password,
    api_get_csrf_token,
    api_login,
    api_logout,
    api_refresh_token,
    api_reset_password,
    api_validate_token,
    resend_verification_email,
    verify_email,
)


def get_auth_routes():
    return [
        Route("/api/auth/login", endpoint=api_login, methods=["POST"]),
        Route("/api/auth/csrf", endpoint=api_get_csrf_token, methods=["GET"]),
        Route(
            "/api/auth/validate-token",
            endpoint=api_validate_token,
            methods=["POST"],
        ),
        Route("/api/auth/refresh", endpoint=api_refresh_token, methods=["POST"]),
        Route("/api/auth/logout", endpoint=api_logout, methods=["POST"]),
        Route(
            "/api/auth/forgot-password",
            endpoint=api_forgot_password,
            methods=["POST"],
        ),
        Route(
            "/api/auth/reset-password",
            endpoint=api_reset_password,
            methods=["POST"],
        ),
        Route("/api/auth/verify-email", endpoint=verify_email, methods=["GET"]),
        Route(
            "/api/auth/resend-verification",
            endpoint=resend_verification_email,
            methods=["POST"],
        ),
    ]
