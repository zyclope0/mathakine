"""Routes API diagnostic adaptatif — F03."""

from starlette.routing import Route

from server.handlers.diagnostic_handlers import (
    complete_diagnostic,
    get_diagnostic_status,
    get_next_question,
    start_diagnostic,
    submit_diagnostic_answer,
)


def get_diagnostic_routes():
    return [
        Route(
            "/api/diagnostic/status",
            endpoint=get_diagnostic_status,
            methods=["GET"],
        ),
        Route(
            "/api/diagnostic/start",
            endpoint=start_diagnostic,
            methods=["POST"],
        ),
        Route(
            "/api/diagnostic/question",
            endpoint=get_next_question,
            methods=["POST"],
        ),
        Route(
            "/api/diagnostic/answer",
            endpoint=submit_diagnostic_answer,
            methods=["POST"],
        ),
        Route(
            "/api/diagnostic/complete",
            endpoint=complete_diagnostic,
            methods=["POST"],
        ),
    ]
