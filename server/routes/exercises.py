"""Routes API exercices."""

from starlette.routing import Route

from server.handlers.exercise_handlers import (
    generate_ai_exercise_stream,
    generate_exercise_api,
    get_completed_exercises_ids,
    get_exercise,
    get_exercises_list,
    get_exercises_stats,
    submit_answer,
)


def get_exercises_routes():
    return [
        Route("/api/exercises", endpoint=get_exercises_list, methods=["GET"]),
        Route(
            "/api/exercises/stats",
            endpoint=get_exercises_stats,
            methods=["GET"],
        ),
        Route(
            "/api/exercises/{exercise_id:int}",
            endpoint=get_exercise,
            methods=["GET"],
        ),
        Route(
            "/api/exercises/generate",
            endpoint=generate_exercise_api,
            methods=["POST"],
        ),
        Route(
            "/api/exercises/generate-ai-stream",
            endpoint=generate_ai_exercise_stream,
            methods=["GET"],
        ),
        Route(
            "/api/exercises/completed-ids",
            endpoint=get_completed_exercises_ids,
            methods=["GET"],
        ),
        Route(
            "/api/exercises/{exercise_id:int}/attempt",
            endpoint=submit_answer,
            methods=["POST"],
        ),
    ]
