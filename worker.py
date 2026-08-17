"""
Cloudflare Worker Entry Point for ScamShield Python Flask Application
Converts Cloudflare Worker Fetch Requests into Flask WSGI calls using a2wsgi.
"""

from app import app
from a2wsgi import WSGIMiddleware

# Wrap Flask WSGI application for Cloudflare Worker ASGI/Pyodide runtime
asgi_app = WSGIMiddleware(app)

async def on_fetch(request, env, ctx):
    """Cloudflare Worker request handler."""
    return await asgi_app(request, env, ctx)
