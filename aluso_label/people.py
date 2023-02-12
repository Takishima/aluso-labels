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

"""People related definitions."""

import dataclasses
import enum
from typing import ClassVar, Union

from dataclasses_json import dataclass_json


class EventParticipation(enum.Flag):
    """Enumeration of event participation types."""

    NOTHING = enum.auto()
    VISIT = enum.auto()
    POST_VISIT = enum.auto()
    APERO = POST_VISIT


@dataclass_json
@dataclasses.dataclass
class Person:
    """A person."""

    aluso_uid: dataclasses.InitVar[str]
    first_name: str
    last_name: str
    is_member: bool
    is_contributor: bool
    participation_type: Union[str, EventParticipation]
    is_committee: bool = dataclasses.field(init=False)

    # NB: This is to be initialized via an environment variable: COMMITTEE_LIST
    COMMITTEE_LIST: ClassVar[set[str]] = set()

    def __post_init__(self, aluso_uid):
        """Post-initialization routine."""
        self.is_committee = aluso_uid in Person.COMMITTEE_LIST

        if not self.is_member and self.is_committee:
            raise RuntimeError('Cannot have a non-member as part of the committee!')
        if not self.is_member and self.is_contributor:
            raise RuntimeError('Cannot have a contributor non-member!')

    @staticmethod
    def from_dict(args):
        """Initialize from a dictionary."""
        person = Person(
            '',
            args['first_name'],
            args['last_name'],
            args['is_member'],
            args['is_contributor'],
            args['participation_type'],
        )
        person.is_committee = args['is_committee']
        return person
