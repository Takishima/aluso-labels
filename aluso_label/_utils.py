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

"""Various helper functions."""

import dataclasses
from typing import Any, Optional

import pydantic

# pylint: disable=no-member


def convert_flat_dataclass_to_pydantic(dcls: type, name: Optional[str] = None) -> type[pydantic.BaseModel]:
    """Convert a dataclass to a pydantic model."""
    if name is None:
        name_ = f"Pydantic{dcls.__name__}"
    else:
        name_ = name
    return pydantic.create_model(  # type: ignore
        name_,
        **_get_pydantic_field_kwargs(dcls),
    )


def _get_pydantic_field_kwargs(dcls: type) -> dict[str, tuple[type, Any]]:
    # get attribute names and types from dataclass into pydantic format
    pydantic_field_kwargs = {}
    for _field in dataclasses.fields(dcls):
        # check is field has default value
        if isinstance(_field.default, dataclasses._MISSING_TYPE):  # pylint: disable=protected-access
            # no default
            default = ...
        else:
            default = _field.default

        pydantic_field_kwargs[_field.name] = (_field.type, default)
    return pydantic_field_kwargs
