import os

from server.src.adapters.inbound.web.app import app

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("VITE_BACKEND_PORT", 4000))
    uvicorn.run(app, host="0.0.0.0", port=port)
