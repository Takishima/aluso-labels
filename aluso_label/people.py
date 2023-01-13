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


class EventParticipation(enum.Flag):
    """Enumeration of event participation types."""

    VISIT = enum.auto()
    POST_VISIT = enum.auto()
    APERO = POST_VISIT


@dataclasses.dataclass
class Person:
    """A person."""

    first_name: str
    last_name: str
    is_contributor: bool
    is_committee: bool
    is_member: bool
    participation_type: EventParticipation

    def __post_init__(self):
        """Post-initialization routine."""
        if not self.is_member and self.is_committee:
            raise RuntimeError('Cannot have a non-member as part of the committee!')
        if not self.is_member and self.is_contributor:
            raise RuntimeError('Cannot have a contributor non-member!')
