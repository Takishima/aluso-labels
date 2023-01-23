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

"""LaTeX generation utilities."""

import re

from flask import redirect, render_template, request, session, url_for

from aluso_label.event import EventFood, EventType
from aluso_label.latex import LABEL_PROPERTIES, Label, generate_latex_document
from aluso_label.people import EventParticipation, Person


def convert_people_list_to_html(people: dict) -> str:
    """Convert a list of people into an HTML table."""
    if not people:
        return ''

    html = (
        '''
        <table>
            <thead>
            <tr>
    '''
        + '\n                    '.join(f'<th>{key}</th>' for key in people[0])
        + r'''
            </tr>
            </thead>
            <tbody>
    '''
    )

    for person in people:
        html += (
            '            <tr>\n'
            + '\n                    '.join(f'<td><pre>{person[data]}</pre></td>' for data in person)
            + '\n            </tr>\n'
        )

    html += r'''
            </tbody>
        </table>
    '''

    return html


def process_people_list():
    """Process a list of participants."""
    try:
        ticket_names = session['ticket_names']
    except KeyError:
        return redirect(url_for('upload_file'))

    if request.method == 'GET':
        ticket_ids = []
        for ticket in ticket_names:
            ticket_ids.append(re.sub(r'[ -/\{}]', '_', ticket.lower()))

        session['ticket_ids'] = ticket_ids

        session['people_csv_html'] = convert_people_list_to_html(session['people'])
        table_labels = [
            f'td:nth-of-type({idx+1}):before {{ content: "{key}"; }}' for idx, key in enumerate(session['people'][0])
        ]
        session['ticket_names_str'] = str(ticket_names)

        return render_template(
            'process.html',
            ticket_ids=ticket_ids,
            str=str,
            zip=zip,
            table_style='\n'.join(table_labels),
            label_properties=[
                (str(label_type), label_props.name) for label_type, label_props in LABEL_PROPERTIES.items()
            ],
        )

    ticket_ids = session['ticket_ids']

    label_type = Label[request.form['label_type'].replace(f'{Label.__name__}.', '')]
    event_type = EventType[request.form['event_type_visit']]
    event_food = EventFood[request.form['event_type_post_visit']]

    ticket_data = {}
    for ticket, uid in zip(ticket_names, ticket_ids):
        participation_type = EventParticipation.NOTHING
        if int(request.form.get(f'{uid}_visit', '0')):
            participation_type |= EventParticipation.VISIT
        if int(request.form.get(f'{uid}_post_visit', '0')):
            participation_type |= EventParticipation.POST_VISIT

        participation_type ^= EventParticipation.NOTHING
        ticket_data[ticket] = participation_type

    people = []
    for person in session['people']:
        person['participation_type'] = ticket_data[person['participation_type']]
        people.append(Person.from_dict(person))

    latex_code = generate_latex_document(label_type, event_type, event_food, people)

    # Clear data from session if successful
    del session['people']
    del session['ticket_names']

    return render_template('overleaf.html', latex_code=latex_code)
