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
from collections.abc import Iterable
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.datastructures import UploadFile
from starlette_wtf import StarletteForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired, StopValidation

from aluso_label.people import Person

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')


class FileRequired(DataRequired):  # pylint: disable=too-few-public-methods
    """Validates that the data is a Werkzeug :class:`~werkzeug.datastructures.FileStorage` object.

    :param message: error message

    You can also use the synonym ``file_required``.
    """

    def __call__(self, form, field):
        """Call operator."""
        if not (isinstance(field.data, UploadFile) and field.data):
            raise StopValidation(self.message or field.gettext("This field is required."))


class FileAllowed:  # pylint: disable=too-few-public-methods
    """Validates that the uploaded file is allowed by a given list of extensions or a Flask-Uploads.

    :param upload_set: A list of extensions or an
        :class:`~flaskext.uploads.UploadSet`
    :param message: error message

    You can also use the synonym ``file_allowed``.
    """

    def __init__(self, upload_set, message=None):
        """Initialise a FileAllowed instance."""
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        """Call operator."""
        if not (isinstance(field.data, UploadFile) and field.data):
            return

        filename = field.data.filename.lower()
        if not filename:
            raise StopValidation('No file specified')

        if isinstance(self.upload_set, Iterable):
            if any(filename.endswith("." + x) for x in self.upload_set):
                return

            raise StopValidation(
                self.message
                or field.gettext("File does not have an approved extension: {extensions}").format(
                    extensions=", ".join(self.upload_set)
                )
            )

        if not self.upload_set.file_allowed(field.data, filename):
            raise StopValidation(self.message or field.gettext("File does not have an approved extension."))


class CSVFileUploadForm(StarletteForm):
    """CSV file input form."""

    csv_file = FileField(label='CSV File', validators=[FileRequired(), FileAllowed(['csv', 'CSV'])])
    submit = SubmitField(label='Upload')


@router.route('/', methods=['GET', 'POST'])
async def upload_file(request: Request):
    """Convert an EPFL Alumni CSV file to a list of participants."""
    form = await CSVFileUploadForm.from_formdata(request)
    if await form.validate_on_submit():
        data_fields = {
            'aluso_uid': ['ID user AF'],
            'first_name': ['Prénom', 'First name'],
            'last_name': ['Nom de famille', 'Family Name'],
            'contribution_status': ['Cotisant', 'Contributeur', 'Contributor'],
            'ticket_name': ['Nom du billet', 'Ticket name'],
        }

        ticket_names = set()
        people = []
        csv_data = await form.csv_file.data.read()
        for row in csv.DictReader(csv_data.decode().splitlines(), skipinitialspace=True):
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
                    return templates.TemplateResponse(
                        'upload.html', {'request': request, 'form': form, 'errors': errors}
                    )

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
                ).to_pydantic()
            )

        request.session.update({'people': jsonable_encoder(people), 'ticket_names': sorted(ticket_names)})
        return RedirectResponse(request.url_for('process_people_list_get'))

    # Something wrong happened -> resubmit current page
    return templates.TemplateResponse('upload.html', {'request': request, 'form': form})
