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


def process_people_list_get(ticket_names, ticket_ids):
    """Process GET requests for the list of participants."""
    session['people_csv_html'] = convert_people_list_to_html(session['people'])
    table_labels = [
        f'td:nth-of-type({idx+1}):before {{ content: "{key}"; }}' for idx, key in enumerate(session['people'][0])
    ]
    session['ticket_names_str'] = str(ticket_names)

    ticket_checkboxes = {'visit': ['checked'] * len(ticket_ids), 'postvisit': [''] * len(ticket_ids)}

    meal_option = EventFood.NOTHING

    for idx, (name, _) in enumerate(zip(ticket_names, ticket_checkboxes['postvisit'])):
        if re.search(r'(avec|with)\s+(repas|souper|d[iî]ner|meal|lunch|dinner)', name, re.IGNORECASE):
            meal_option = EventFood.MEAL if meal_option == EventFood.NOTHING else meal_option
            ticket_checkboxes['postvisit'][idx] = 'checked'
        elif re.search(r'(avec|with)\s+ap[eé]ro', name, re.IGNORECASE):
            meal_option = EventFood.APERO if meal_option == EventFood.NOTHING else meal_option
            ticket_checkboxes['postvisit'][idx] = 'checked'
        elif re.search(r'visite?\s+(seule|uniquement|only)', name, re.IGNORECASE):
            pass

    meal_radio_button = {'no_meal': '', 'apero': '', 'meal': ''}
    if meal_option == EventFood.MEAL:
        meal_radio_button['meal'] = 'checked'
    elif meal_option == EventFood.APERO:
        meal_radio_button['apero'] = 'checked'
    else:
        meal_radio_button['no_meal'] = 'checked'

    return render_template(
        'process.html',
        ticket_ids=ticket_ids,
        ticket_visit_checked=ticket_checkboxes['visit'],
        ticket_postvisit_checked=ticket_checkboxes['postvisit'],
        no_meal_checked=meal_radio_button['no_meal'],
        apero_checked=meal_radio_button['apero'],
        meal_checked=meal_radio_button['meal'],
        str=str,
        zip=zip,
        table_style='\n'.join(table_labels),
        label_properties=[(str(label_type), label_props.name) for label_type, label_props in LABEL_PROPERTIES.items()],
    )


def process_people_list_post(ticket_names, ticket_ids):
    """Process POST requests for the list of participants."""
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

    latex_code = generate_latex_document(
        Label[request.form['label_type'].replace(f'{Label.__name__}.', '')],
        EventType[request.form['event_type_visit']],
        EventFood[request.form['event_type_post_visit']],
        people,
    )

    # Clear data from session if successful
    del session['people']
    del session['ticket_names']

    return render_template('overleaf.html', latex_code=latex_code)


def process_people_list():
    """Process a list of participants."""
    try:
        ticket_names = session['ticket_names']
    except KeyError:
        return redirect(url_for('upload_file'))

    ticket_ids = [re.sub(r'[ -/\{}]', '_', name.lower()) for name in ticket_names]

    if request.method == 'GET':
        return process_people_list_get(ticket_names, ticket_ids)
    return process_people_list_post(ticket_names, ticket_ids)
