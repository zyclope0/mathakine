"""Routes diverses : analytics, feedback, recommendations, chat."""

from starlette.routing import Route

from server.handlers.analytics_handlers import analytics_event
from server.handlers.chat_handlers import chat_api, chat_api_stream
from server.handlers.feedback_handlers import submit_feedback
from server.handlers.recommendation_handlers import (
    generate_recommendations,
    get_recommendations,
    handle_recommendation_complete,
)


def get_misc_routes():
    return [
        Route(
            "/api/analytics/event",
            endpoint=analytics_event,
            methods=["POST"],
        ),
        Route(
            "/api/feedback",
            endpoint=submit_feedback,
            methods=["POST"],
        ),
        Route(
            "/api/recommendations",
            endpoint=get_recommendations,
            methods=["GET"],
        ),
        Route(
            "/api/recommendations/generate",
            endpoint=generate_recommendations,
            methods=["POST"],
        ),
        Route(
            "/api/recommendations/complete",
            endpoint=handle_recommendation_complete,
            methods=["POST"],
        ),
        Route("/api/chat", endpoint=chat_api, methods=["POST"]),
        Route("/api/chat/stream", endpoint=chat_api_stream, methods=["POST"]),
    ]
