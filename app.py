from flask import Flask
from flask_sitemap import Sitemap

# flask --app app run --debug

# Site map extension.
ext = Sitemap()


# Application factory.
def create_app(test_config=None):
    app = Flask(__name__)
    ext.init_app(app)

    # Register routes
    from routes import register_routes
    register_routes(app)

    return app
