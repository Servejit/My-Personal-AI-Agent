"""Independent Poster Maker task app."""
from core.services import *
from tasks import _poster_renderer

TASK_NAME = "Poster Maker"
TASK_ICON = "🖼️"

def render():
    _poster_renderer.render()
