from flask import request, Response, redirect, render_template, send_file, url_for
from application.json_parser import parse_json_structures
from application.class_generator import ClassGenerator
from time import time
from app import ext


def register_routes(app):  # noqa: C901
    @app.route("/")
    def index():
        return redirect(url_for("php"))

    @app.route("/php", methods=['GET', 'POST'])
    def php():
        classes, error = {}, None

        if request.method == 'POST':
            generator, classes, error = parse_classes('php')
            if request.form.get("action") == 'download':
                return prepare_zip_response(generator, classes, 'php')

        return render_template("index.html", route="php", classes=classes, error=error)

    @app.route("/java", methods=['GET', 'POST'])
    def java():
        classes, error = {}, None

        if request.method == 'POST':
            generator, classes, error = parse_classes('java')
            if request.form.get("action") == 'download':
                return prepare_zip_response(generator, classes, 'java')

        return render_template("index.html", route="java", classes=classes, error=error)

    @app.route("/python", methods=['GET', 'POST'])
    def python():
        classes, error = {}, None

        if request.method == 'POST':
            generator, classes, error = parse_classes('python')
            if request.form.get("action") == 'download':
                return prepare_zip_response(generator, classes, 'py')

        return render_template("index.html", route="python", classes=classes, error=error)

    # Sitemap extension static routes generator
    @ext.register_generator
    def static_sitemap():
        yield 'php', {}
        yield 'java', {}
        yield 'python', {}


def parse_classes(language: str) -> tuple:
    models, error = parse_json_structures(request.form["json_full"], request.form["json_min"])
    generator = ClassGenerator(models)
    classes = getattr(generator, f"generate_{language}_classes")()
    return generator, classes, error


def prepare_zip_response(generator: ClassGenerator, classes: dict, language_extension: str) -> Response:
    return send_file(
        generator.create_zip_response(classes, language_extension),
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{language_extension}_classes_{int(time())}.zip"
    )
