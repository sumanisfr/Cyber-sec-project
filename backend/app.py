import logging
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_wtf.csrf import generate_csrf
from dotenv import load_dotenv

from database import init_db
from extensions import csrf, jwt, limiter
from scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)


def create_app():
    frontend_build_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
    app = Flask(__name__, static_folder=None)

    # Load environment variables from .env
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_EXPIRES_SECONDS', 3600))
    app.config['WTF_CSRF_TIME_LIMIT'] = None

    # Security middleware
    CORS(app, supports_credentials=True)
    jwt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register blueprints for modules
    from api.malware import malware_bp
    from api.vuln import vuln_bp
    from api.stats import stats_bp
    from api.job_scam import job_scam_bp
    from auth.routes import auth_bp

    init_db()
    app.register_blueprint(malware_bp, url_prefix='/api/malware')
    app.register_blueprint(vuln_bp, url_prefix='/api/vuln')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(job_scam_bp, url_prefix='/api/job-scam')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Serve frontend routes in production build, while leaving /api/* to the API blueprints.
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        if path.startswith('api/'):
            return jsonify({'error': 'API route not found'}), 404

        static_path = os.path.join(frontend_build_dir, path)
        if path and os.path.exists(static_path) and os.path.isfile(static_path):
            return send_from_directory(frontend_build_dir, path)
        return send_from_directory(frontend_build_dir, 'index.html')

    @app.route('/api/auth/csrf-token', methods=['GET'])
    def csrf_token():
        # Frontend can use this to send a CSRF token back in X-CSRFToken header.
        return jsonify({'csrf_token': generate_csrf()})

    # Start background scheduler for periodic scans
    start_scheduler(app)

    return app


if __name__ == '__main__':
    app = create_app()

    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database schema."""
        init_db()
        print('Initialized the database.')

    app.run(debug=True)
