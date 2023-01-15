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

    left: float
    right: float
    top: float
    bottom: float


_DEFAULT_LABEL_MARGIN = Margin(5, 5, 5, 5)


class LabelProperties(NamedTuple):
    """Definition of a set of label properties."""

    name: str
    width: float
    height: float
    cols: int
    rows: int
    page_margin: Margin
    inter_col: float
    inter_row: float
    label_margin: Margin = _DEFAULT_LABEL_MARGIN

    def __str__(self):
        """Generate the LaTeX code for a given label geometry."""
        return textwrap.dedent(
            rf'''
        % Label configuration for: {self.name}
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

    AVERY_635X2963 = enum.auto()
    AVERY_646X338 = enum.auto()
    AVERY_64X36 = enum.auto()
    AVERY_70X32 = enum.auto()
    AVERY_70X35 = enum.auto()
    AVERY_70X36 = enum.auto()
    AVERY_70X37 = enum.auto()
    AVERY_70X41 = enum.auto()
    AVERY_70X423 = enum.auto()
    AVERY_80X50 = enum.auto()


LABEL_PROPERTIES = {
    Label.AVERY_635X2963: LabelProperties(
        '63.5x29.63mm (L4784)', 63.5, 29.63, 3, 9, Margin(7.2, 7.2, 15.15, 15.15), 2.5, 0
    ),
    Label.AVERY_646X338: LabelProperties(
        '64.6x33.8mm (A3658/A6172)', 64.6, 33.8, 3, 8, Margin(8.1, 8.1, 13.3, 13.3), 0, 0
    ),
    Label.AVERY_64X36: LabelProperties('64x36mm (A3670,A6170)', 64, 36, 3, 7, Margin(9, 9, 22.5, 22.5), 0, 0),
    Label.AVERY_70X32: LabelProperties('70x32mm (A3479)', 70, 32, 3, 9, Margin(0, 0, 4.5, 4.5), 0, 0),
    Label.AVERY_70X35: LabelProperties('70x35mm (A3422)', 70, 35, 3, 8, Margin(0, 0, 4.5, 4.5), 0, 0),
    Label.AVERY_70X36: LabelProperties('70x36mm (A3475,A3490,A6122)', 70, 36, 3, 8, Margin(0, 0, 5, 4), 0, 0),
    Label.AVERY_70X37: LabelProperties('70x37mm (A3474,A6173)', 70, 37, 3, 8, Margin(0, 0, 0.5, 0.5), 0, 0),
    Label.AVERY_70X41: LabelProperties('70x41mm (A3481)', 70, 41, 3, 7, Margin(0, 0, 5, 5), 0, 0),
    Label.AVERY_70X423: LabelProperties('70x42.3mm (A3652/A6174)', 70, 42.3, 3, 7, Margin(0, 0, 0.45, 0.45), 0, 0),
    Label.AVERY_80X50: LabelProperties('80x50mm (L/J4785)', 80, 50, 2, 5, Margin(17.4, 17.4, 12.6, 14.3), 15, 5),
}

# ==============================================================================
