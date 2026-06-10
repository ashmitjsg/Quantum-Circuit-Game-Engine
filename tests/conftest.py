"""Test configuration.

Force SDL's dummy video/audio drivers so importing pygame (pulled in by ``qcge``)
works on headless CI runners without a display or sound card.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
