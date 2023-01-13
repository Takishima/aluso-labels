#   Copyright 2023 <Damien Nguyen>
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
#   documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
#   Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#   WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
#   OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#   OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Main for Flask app."""

import csv
import os
import pprint
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request
from werkzeug.utils import secure_filename

from aluso_label.people import Person


def create_app(test_config=None):
    """Create and configure the application."""
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_mapping(SECRET_KEY='dev')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello World!'

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        _error = render_template('error.html'), {'Refresh': f'5; {request.url}'}

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file in request!')
                return _error

            file = request.files['file']
            if file.filename == '':
                flash('No selected file!', 'error')
                return _error

            filename = Path(file.filename)
            if not file or filename.suffix not in ('.CSV', '.csv'):
                flash('Uh-oh! Unsupported file extension and/or something unexpected happened!')
                return _error

            data_fields = {
                'aluso_uid': ['ID user AF'],
                'transation_uid': ['ID transaction/autorisation', 'Transaction/Authorization ID'],
                'first_name': ['Prénom', 'First name'],
                'last_name': ['Nom de famille', 'Family Name'],
                'contribution_status': ['Cotisant', 'Contributor'],
                'ticket_name': ['Nom du billet', 'Ticket name'],
            }

            people = []
            for row in csv.DictReader(file.read().decode().splitlines(), skipinitialspace=True):
                current_data = {}
                for field, options in data_fields.items():
                    for option in options:
                        if option in row:
                            current_data[field] = row[option].strip()
                            break
                    else:
                        raise RuntimeError(f'Unable to parse CSV data for field {field} (tried {options})')
                if not current_data['ticket_name']:
                    # There are sometimes some double entries with identical data except empty ticket name
                    continue

                people.append(
                    Person(
                        current_data['aluso_uid'],
                        current_data['first_name'],
                        current_data['last_name'],
                        current_data['contribution_status'] != '',
                        current_data['contribution_status'] in ('Oui', 'Yes'),
                        current_data['ticket_name'],
                    )
                )

            return render_template('upload.html', filestring=pprint.pformat(people, indent=4))

        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''

    return app
