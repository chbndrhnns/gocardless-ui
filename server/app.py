import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from server.routes.sync_routes import sync_bp, schedule_sync
from server.services.sync_service import (
    get_token_storage,
)
from .routes.accounts_routes import accounts_bp
from .routes.auth_routes import auth_bp
from .routes.institutions_routes import institutions_bp
from .routes.lunchmoney_routes import lunchmoney_bp
from .routes.requisitions_routes import requisitions_bp

# Load environment variables
load_dotenv()

app = Flask(__name__, instance_relative_config=True)
CORS(
    app,
    resources={
        r"/api/*": {"origins": os.getenv("BACKEND_CORS_ORIGINS")},
    },
)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(requisitions_bp, url_prefix="/api/requisitions")
app.register_blueprint(institutions_bp, url_prefix="/api/institutions")
app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
app.register_blueprint(lunchmoney_bp, url_prefix="/api/lunchmoney")
app.register_blueprint(sync_bp, url_prefix="/api/sync")

if __name__ == "__main__":
    schedule_sync(get_token_storage())
    port = int(os.getenv("BACKEND_PORT", 4000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
