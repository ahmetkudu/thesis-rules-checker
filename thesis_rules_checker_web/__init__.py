import os
import io

import flask
from flask import Flask

import thesis_rules_checker
import fitz


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return flask.send_from_directory('static', 'index.html')

    @app.route('/check', methods=['POST'])
    def check():
        file = flask.request.files['file']
        document = fitz.open(stream=file.stream.read(), filetype='pdf')
        thesis_rules_checker.process_document(document)
        return flask.send_file(
            io.BytesIO(document.write()),
            as_attachment=True,
            download_name=thesis_rules_checker.get_output_filename(file.filename))

    return app
