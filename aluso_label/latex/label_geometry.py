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

"""Label geometry utilities."""

import enum
import textwrap
from typing import NamedTuple

# ==============================================================================


class Margin(NamedTuple):
    """An object margin on a page."""

    left: int
    right: int
    top: int
    bottom: int


_DEFAULT_LABEL_MARGIN = Margin(5, 5, 5, 5)


class LabelGeometry(NamedTuple):
    """Definition of a set of label properties."""

    cols: int
    rows: int
    page_margin: Margin
    inter_col: int
    inter_row: int
    label_margin: Margin = _DEFAULT_LABEL_MARGIN

    def __str__(self):
        """Generate the LaTeX code for a given label geometry."""
        return textwrap.dedent(
            rf'''
        \LabelCols={self.cols}
        \LabelRows={self.rows}
        \LeftPageMargin={self.page_margin.left}mm
        \RightPageMargin={self.page_margin.right}mm
        \TopPageMargin={self.page_margin.top}mm
        \BottomPageMargin={self.page_margin.bottom}mm
        \InterLabelColumn={self.inter_col}mm
        \InterLabelRow={self.inter_row}mm
        \LeftLabelBorder={self.label_margin.left}mm
        \RightLabelBorder={self.label_margin.right}mm
        \TopLabelBorder={self.label_margin.top}mm
        \BottomLabelBorder={self.label_margin.bottom}mm
        \LabelSetup
        '''
        )


# ==============================================================================


class Label(enum.Enum):
    """Types of label."""

    AVERY_646X338 = enum.auto()
    AVERY_64X36 = enum.auto()
    AVERY_70X32 = enum.auto()
    AVERY_70X35 = enum.auto()
    AVERY_70X36 = enum.auto()
    AVERY_70X37 = enum.auto()
    AVERY_70X41 = enum.auto()
    AVERY_70X423 = enum.auto()


LABEL_GEOMETRY = {
    Label.AVERY_646X338: LabelGeometry(3, 8, Margin(8.1, 8.1, 13.3, 13.3), 0, 0),
    Label.AVERY_64X36: LabelGeometry(3, 7, Margin(9, 9, 22.5, 22.5), 0, 0),
    Label.AVERY_70X32: LabelGeometry(3, 9, Margin(0, 0, 4.5, 4.5), 0, 0),
    Label.AVERY_70X35: LabelGeometry(3, 8, Margin(0, 0, 4.5, 4.5), 0, 0),
    Label.AVERY_70X36: LabelGeometry(3, 8, Margin(0, 0, 5, 4), 0, 0),
    Label.AVERY_70X37: LabelGeometry(3, 8, Margin(0, 0, 0.5, 0.5), 0, 0),
    Label.AVERY_70X41: LabelGeometry(3, 7, Margin(0, 0, 5, 5), 0, 0),
    Label.AVERY_70X423: LabelGeometry(3, 7, Margin(0, 0, 0.45, 0.45), 0, 0),
}

# ==============================================================================
