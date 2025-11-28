"""
Mathakine server module.

This package provides a modular architecture for the Mathakine server,
organizing functionality into cohesive modules.
"""

# Expose key functions from modules for easier imports
from server.app import create_app, run_server
from server.database import get_database_url, init_database
from server.template_handler import render_error, render_template

__all__ = [
    'create_app',
    'run_server',
    'render_template',
    'render_error',
    'init_database',
    'get_database_url',
] 