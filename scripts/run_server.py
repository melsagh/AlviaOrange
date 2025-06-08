"""Start the AlviaOrange HTTP server."""

from __future__ import annotations

import uvicorn

from alviaorange.server import app


if __name__ == "__main__":  # pragma: no cover - manual entry
    uvicorn.run(app, host="0.0.0.0", port=8000)
