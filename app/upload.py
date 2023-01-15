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

"""CSV file upload utilities."""

import csv

from flask import redirect, render_template, session, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import FileField, SubmitField

from aluso_label.people import Person


class CSVFileUploadForm(FlaskForm):
    """CSV file input form."""

    csv_file = FileField(label='CSV File', validators=[FileRequired(), FileAllowed(['csv', 'CSV'])])
    submit = SubmitField(label='Upload')


def upload_file():
    """Convert an EPFL Alumni CSV file to a list of participants."""
    form = CSVFileUploadForm()
    if form.validate_on_submit():
        data_fields = {
            'aluso_uid': ['ID user AF'],
            'transation_uid': ['ID transaction/autorisation', 'Transaction/Authorization ID'],
            'first_name': ['Prénom', 'First name'],
            'last_name': ['Nom de famille', 'Family Name'],
            'contribution_status': ['Cotisant', 'Contributor'],
            'ticket_name': ['Nom du billet', 'Ticket name'],
        }

        ticket_names = set()
        people = []
        for row in csv.DictReader(form.csv_file.data.read().decode().splitlines(), skipinitialspace=True):
            current_data = {}
            for field, options in data_fields.items():
                for option in options:
                    if option in row:
                        current_data[field] = row[option].strip()
                        break
                else:
                    options = [f'"{option}"' for option in options]
                    form.form_errors = [f'Unable to parse CSV data for field {field} (tried {", ".join(options)})']
                    errors = [
                        ('p', form.form_errors[0]),
                        ('p', ' '),
                        (
                            'p',
                            (
                                'Are you sure you that any of the columns listed '
                                'below were selected when exporting the CSV file?'
                            ),
                        ),
                        ('li', options),
                    ]
                    return render_template('upload.html', form=form, errors=errors)

            if not current_data['ticket_name']:
                # There are sometimes some double entries with identical data except empty ticket name
                continue

            ticket_names.add(current_data['ticket_name'])
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

        ticket_names = sorted(ticket_names)

        session['people'] = people
        session['ticket_names'] = ticket_names
        return redirect(url_for('process_people_list'))

    # Something wrong happened -> resubmit current page
    return render_template('upload.html', form=form)
