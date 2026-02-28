"""Routes API défis logiques."""

from starlette.routing import Route

from server.handlers.challenge_handlers import (
    generate_ai_challenge_stream,
    get_challenge,
    get_challenge_hint,
    get_challenges_list,
    get_completed_challenges_ids,
    submit_challenge_answer,
)


def get_challenges_routes():
    return [
        Route(
            "/api/challenges",
            endpoint=get_challenges_list,
            methods=["GET"],
        ),
        Route(
            "/api/challenges/{challenge_id:int}",
            endpoint=get_challenge,
            methods=["GET"],
        ),
        Route(
            "/api/challenges/{challenge_id:int}/attempt",
            endpoint=submit_challenge_answer,
            methods=["POST"],
        ),
        Route(
            "/api/challenges/{challenge_id:int}/hint",
            endpoint=get_challenge_hint,
            methods=["GET"],
        ),
        Route(
            "/api/challenges/completed-ids",
            endpoint=get_completed_challenges_ids,
            methods=["GET"],
        ),
        Route(
            "/api/challenges/generate-ai-stream",
            endpoint=generate_ai_challenge_stream,
            methods=["GET"],
        ),
    ]
