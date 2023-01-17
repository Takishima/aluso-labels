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

import os

from flask import Flask

from aluso_label.people import Person

from .process import process_people_list
from .upload import upload_file


def add_version_info_to_template():
    """Flask context processor to automatically add some variables to the base template."""
    version = os.environ.get('VERCEL_GIT_COMMIT_SHA', 'N/A')
    if not version:
        version = 'N/A'
    return {'version': version}


def create_app():
    """Create and configure the application."""
    aluso_app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    aluso_app.config.from_mapping(SECRET_KEY='dev')
    aluso_app.config.from_prefixed_env()

    Person.COMMITTEE_LIST = {uid.strip() for uid in aluso_app.config.get('COMMITTEE_LIST', '').split(',')}

    aluso_app.add_url_rule('/', view_func=upload_file, methods=['GET', 'POST'])
    aluso_app.add_url_rule('/process', view_func=process_people_list, methods=['GET', 'POST'])
    aluso_app.context_processor(add_version_info_to_template)
    return aluso_app


if __name__ == '__main__':
    app = create_app()
    app.run()
