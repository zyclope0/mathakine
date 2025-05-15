"""
Mathakine server module.

This package provides a modular architecture for the Mathakine server,
organizing functionality into cohesive modules.
"""

# Expose key functions from modules for easier imports
from server.app import create_app, run_server
from server.template_handler import render_template, render_error
from server.database import init_database, get_database_url

__all__ = [
    'create_app',
    'run_server',
    'render_template',
    'render_error',
    'init_database',
    'get_database_url',
] 