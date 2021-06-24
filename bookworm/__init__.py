import os

from flask import Flask, request, render_template, jsonify, current_app


def create_app(test_config=None):

    app = Flask(__name__)

    if test_config is None:
        app.config.from_mapping(
            DATABASE=os.path.join(app.instance_path, 'bookworm.db'),
        )
    else:
        app.config.from_mapping(
            DATABASE=os.path.join(app.instance_path, 'bookworm_test.db'),
        )
        app.config.from_mapping(test_config)
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db_orm
    db_orm.configure_session(app)
    
    from . import books
    from . import members
    from . import bookissue
    from . import frappe_api
    from . import lms
    app.register_blueprint(lms.api)
    app.register_blueprint(lms.app)

    @app.route("/hello.json", methods=['GET', 'POST'])
    def hello():
        return jsonify(greetings='Hello World')

    return app
