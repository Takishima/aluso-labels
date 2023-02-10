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

"""Main for FastAPI app."""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings
from starlette.middleware.sessions import SessionMiddleware

from aluso_label.people import Person

try:
    from . import help_page, process, upload
except ImportError:
    from app import help_page, process, upload


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Settings handler for web app."""

    secret_key: str = 'dev'
    committee_list: list[str]


def add_version_info_to_template():
    """Flask context processor to automatically add some variables to the base template."""
    version = os.environ.get('VERCEL_GIT_COMMIT_SHA', 'N/A')
    if not version:
        version = 'N/A'
    return {'version': version}


app = FastAPI(debug=True)

settings = Settings()
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
Person.COMMITTEE_LIST = set(settings.committee_list)

app.mount("/static", StaticFiles(packages=[(__name__, 'static')]), name='static')

app.include_router(upload.router)
app.include_router(help_page.router)
