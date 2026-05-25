#!/usr/bin/env python3
"""Hivemind — AI Debate Platform. Run the API server."""
import uvicorn
if __name__ == "__main__":
    uvicorn.run("hivemind.api.server:app", host="0.0.0.0", port=8000, reload=True)
