from flask import Flask, request, redirect, render_template, send_file, url_for
from application.json_parser import parse_json_structures
from application.class_generator import ClassGenerator
from time import time


# flask --app app run --debug

# Application factory.
def create_app(test_config=None):
    app = Flask(__name__)

    @app.route("/")
    def start():
        return redirect(url_for("php"))

    @app.route("/php", methods=['GET', 'POST'])
    def php():
        classes, error = {}, None

        if request.method == 'POST':
            models, error = parse_json_structures(request.form["json_full"], request.form["json_min"])
            generator = ClassGenerator(models)
            classes = generator.generate_php_classes()
            # Return zipped response in case download button clicked.
            if request.form.get("action") == 'download':
                return send_file(
                    generator.create_zip_response(classes, "php"),
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"php_classes_{int(time())}.zip"
                )

        return render_template("index.html", route="php", classes=classes, error=error)

    @app.route("/java", methods=['GET', 'POST'])
    def java():
        classes, error = {}, None

        if request.method == 'POST':
            models, error = parse_json_structures(request.form["json_full"], request.form["json_min"])
            generator = ClassGenerator(models)
            classes = generator.generate_java_classes()
            # Return zipped response in case download button clicked.
            if request.form.get("action") == 'download':
                return send_file(
                    generator.create_zip_response(classes, "java"),
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"java_classes_{int(time())}.zip"
                )

        return render_template("index.html", route="java", classes=classes, error=error)

    @app.route("/python", methods=['GET', 'POST'])
    def python():
        classes, error = {}, None

        if request.method == 'POST':
            models, error = parse_json_structures(request.form["json_full"], request.form["json_min"])
            generator = ClassGenerator(models)
            classes = generator.generate_python_classes()
            # Return zipped response in case download button clicked.
            if request.form.get("action") == 'download':
                return send_file(
                    generator.create_zip_response(classes, "py"),
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"python_classes_{int(time())}.zip"
                )

        return render_template("index.html", route="python", classes=classes, error=error)

    return app
