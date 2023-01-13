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

"""LaTeX utilities."""

import textwrap

from ..event import EventType
from ..people import EventParticipation, Person
from .label_geometry import LABEL_GEOMETRY, Label

# ==============================================================================


def apply_stretch_factor(string: str, ref_length: int, threshold: float = 0.5) -> str:
    """Modify LaTeX string with a stretch factor if necessary.

    This is mostly useful when handling very long names in order to make sure that the characters on the output label do
    notgo out of bounds when printing the labels.

    Args:
        string (str): Input string
        ref_length (int): Reference length (ie. maximum allowed number of characters)
        threshold (float): Minimum value for the stretch factor before giving up
    """
    if len(string) > ref_length:
        stretch = ref_length / len(string)
        if stretch < threshold:
            raise RuntimeError(f'Too small stretch factor {stretch} for `{string}` given ref. length {ref_length}')
        return rf'{{\addfontfeatures{{FakeStretch={stretch}}}{string}}}'
    return string


def person_to_latex(person: Person, label_type: Label) -> str:
    """Serialize a Person into LaTeX."""
    ref_length = 13
    if label_type in (Label.AVERY_64X36, Label.AVERY_646X338):
        ref_length = 12

    first_name = apply_stretch_factor(person.first_name, ref_length)
    last_name = apply_stretch_factor(person.last_name, ref_length)

    if person.is_contributor:
        member_icon = r'\contribIcon'
    elif person.is_member:
        member_icon = r'\memberIcon'
    else:
        member_icon = r'\externalIcon'

    if person.is_committee:
        member_icon += r'\ \committee'

    if EventParticipation.VISIT in person.participation_type:
        visit_icon = r'\visitIcon'
    else:
        visit_icon = r'\emptyIcon'

    if EventParticipation.POST_VISIT in person.participation_type:
        post_visit_icon = r'\postVisitIcon'
    else:
        post_visit_icon = r'\emptyIcon'

    return rf'\addPerson{{{first_name}}}{{{last_name}}}{{{member_icon}}}{{{visit_icon}}}{{{post_visit_icon}}}'


# ==============================================================================


class LatexDocument:
    """A LaTeX document."""

    HEADER = ''

    ICON_APERO = ''
    ICON_COMMITTEE = ''
    ICON_CONTRIBUTOR = ''
    ICON_EXTERNAL = ''
    ICON_MEAL = ''
    ICON_MEMBER = ''
    ICON_VISIT = ''

    def __init__(self, label: Label, event_type: EventType):
        """Initialize a LaTeX document instance.

        Args:
            label (Label): Type of label to generate
            event_type (EventType): Type of event
        """
        self._label_type = label
        self._event_type = event_type

        self._generate_header()

    def generate(self, people: list[Person]) -> str:
        """Generate a LaTeX document."""
        text = f'{self._header}' + textwrap.dedent(
            r'''
        \begin{document}
          \begin{labels}
'''
        )

        for person in people:
            text += f'    {person_to_latex(person, self._label_type)}\n\n'

        return (
            text
            + r'''  \end{labels}
\end{document}
'''
        )

    @property
    def event_type(self) -> EventType:
        """Getter for the event type."""
        return self._event_type

    @event_type.setter
    def event_type(self, new_type: EventType):
        self._event_type = new_type
        self._generate_header()

    @property
    def label_type(self) -> Label:
        """Getter for the label type."""
        return self._label_type

    @label_type.setter
    def label_type(self, new_type: Label):
        self._label_type = new_type
        self._generate_header()

    def _generate_header(self):
        """Generate LaTeX header."""
        visit_icon = r'\emptyIcon'

        post_visit_icon = r''
        if EventType.APERO in self._event_type:
            post_visit_icon = LatexDocument.ICON_APERO
        if EventType.DINNER in self._event_type:
            post_visit_icon = LatexDocument.ICON_MEAL

        self._header = LatexDocument.HEADER.format(
            label_type=LABEL_GEOMETRY[self._label_type], visit=visit_icon, post_visit=post_visit_icon
        )

        self._header += textwrap.dedent(
            r'''
    % Label macros
    \newcommand{\addPerson}[5]{%
      % Arguments: <first_name> <last_name> <member_icons> <visit_icon> <post_visit_icon>
      \insertEPFLAlumniLogo%
      \begin{minipage}{\personDataWidth}
        \large #1\\#2
      \end{minipage}

      \vspace{.5ex}

      \begin{minipage}[b]{\logoWidth}
        #3
      \end{minipage}%
      \begin{minipage}[b]{\personDataWidth}
        '''
        )

        if EventType.VISIT in self._event_type:
            self._header += r'    #4\ #5'
        else:
            self._header += r'    #5'  # NB: we skip the 'visit' icon if there's no visit

        self._header += textwrap.dedent(
            r'''
      \end{minipage}
    }

    % ==============================================================================
'''
        )


# ==============================================================================
# NB: These icons do not need to have the '{' and '}' protected

LatexDocument.ICON_APERO = textwrap.dedent(
    r'''%
      \begin{tikzpicture}[scale=0.02]
        \draw[] (7.5,10) circle (4);
        \draw[fill=white,] (0,0) -- ++(-7.5,10) -- ++(15,0) -- cycle;
        %               ((12.5-r)*0.6, (12.5-r)*0.8)
        \draw[] (0,0) -- ++(-5.1,6.8) -- ++(10.2,0) -- cycle
        (0,0) -- ++(0,-8.5) -- ++(-4,0) -- ++(8,0);
      \end{tikzpicture}%'''
)

LatexDocument.ICON_MEAL = textwrap.dedent(
    r'''%
      \begin{tikzpicture}[scale=0.0048]
        \draw (0,-35) -- (0,0) -- ++(56,0) -- ++(0,-35) arc (0:-90:24) -- ++(0, -20) arc (-180:-90:15) -- ++(5,0);
        \draw (0,-35) arc (180:270:24) -- ++(0, -20) arc (0:-90:15) -- ++(-5,0);
        \draw (56,0) ++ (12,0) -- +(0,-26) ++(12,0) -- +(0,-26) ++(12,0) -- +(0,-30) arc (0:-90:12) -- +(0,-52);
      \end{tikzpicture}%'''
)

# ------------------------------------------------------------------------------

LatexDocument.ICON_COMMITTEE = textwrap.dedent(
    r'''%
      \begin{{tikzpicture}}[scale=0.01, color=epflred]
        \draw (10, 0) arc (180:0:10) (20,15) circle (5);
        \draw (30, 0) arc (180:0:10) (40,15) circle (5);
        \draw (50, 0) arc (180:0:10) (60,15) circle (5);
        \draw rectangle (0, 0) rectangle (80,-10);
        \draw (10, -11) -- (10, -30) -- (70, -30) -- (70,-11);
      \end{{tikzpicture}}%'''
)

LatexDocument.ICON_CONTRIBUTOR = textwrap.dedent(
    r'''%
      \begin{{tikzpicture}}[x=.2mm,y=.2mm]
        \draw[] (0,0) -- (0, 9) +(2.6, 0) -- +(2.6,-9) +(-2.6,0) -- +(-2.6,-9)
              (-5.2,0) -- ++(0, 18) (5.2,0) -- ++(0,18)
              (-5.2,11) -- (5.2,11) (-5.2,13.7) -- (5.2,13.7);
              \pgfmathsetmacro{{\domain}}{{pi*91/180+2*pi}}
        \draw [shift={{(7.07,18.3)}}, domain=0:\domain, variable=\t,
               smooth, samples=int(100)] plot ({{\t r}}: {{4.5*\t/\domain}});
        \draw [shift={{(-7.07,18.3)}}, domain=0:\domain, variable=\t,
               smooth, samples=int(100)] plot ({{-\t r}}: {{-4.5*\t/\domain}});
        \draw[] (-7.05,22.8) -- (7.05,22.8);
      \end{{tikzpicture}}%'''
)

LatexDocument.ICON_EXTERNAL = textwrap.dedent(
    r'''%
      \begin{{tikzpicture}}[scale=0.02]
        % 11 = 7 (radius arc) + 4 (radius circle)
        \draw (0, 5) arc (180:0:7) ++(-7, 11) circle (4);
        \draw (0, 5) -- (0, 0) -- ++(14, 0) -- ++(0, 5);
      \end{{tikzpicture}}%'''
)

LatexDocument.ICON_MEMBER = textwrap.dedent(
    r'''%
      \begin{{tikzpicture}}[scale=0.02]
        % NB: 11 = 7 (radius arc) + 4 (radius circle)
        \draw (0, 5) arc (180:0:7) ++(-7, 11) circle (4);
        \draw (0, 5) -- (0, 0) -- ++(14, 0) -- ++(0, 5);
      \end{{tikzpicture}}%'''
)

LatexDocument.HEADER = textwrap.dedent(
    rf'''
    \documentclass[a4paper,12pt]{{{{article}}}}
    \usepackage{{{{fontspec,graphicx,xcolor,tikz,varwidth}}}}
    \usepackage[newdimens]{{{{labels}}}}
    \setmainfont{{{{Arial}}}}
    % ==============================================================================
    {{label_type}}
    %\LabelGridtrue % uncomment if you want to have the outline of the labels

    % ==============================================================================
    % Annotation macros
    \newcommand{{{{\visit}}}}{{{{\contribIcon}}}}     % may be changed to anything ;-)
    \newcommand{{{{\postVisit}}}}{{{{\postVisitIcon}}}} % may be changed to anything ;-)
    \newcommand{{{{\committee}}}}{{{{\committeeIcon}}}} % may be changed to anything ;-)

    % ==============================================================================
    % Dimensions definition
    \makeatletter
    \newlength{{{{\logoWidth}}}}
    \newlength{{{{\personDataWidth}}}}
    \setlength{{{{\logoWidth}}}}{{{{2.4cm}}}} % might try adjusting this if your results aren\'t perfect...
    \setlength{{{{\personDataWidth}}}}{{{{\area@width}}}}
    \addtolength{{{{\personDataWidth}}}}{{{{-\logoWidth}}}}
    \makeatother

    % ==============================================================================
    % Color definitions
    \definecolor{{{{epflred}}}}{{{{rgb}}}}{{{{1,0,0}}}}  % official EPFL red (web)
    \definecolor{{{{accblue}}}}{{{{rgb}}}}{{{{0.25,0,1}}}}       % blue for accompanying people

    % ==============================================================================
    % Marks and icons
    \newcommand{{{{\swissFlagIcon}}}}{{{{%
      \begin{{{{tikzpicture}}}}[scale=0.0025]
      \fill[red] (0,0) rectangle (110,110);
     '\fill[white] (43,15) rectangle (67,95);
      \fill[white] (15,67) rectangle (95,43);
      \end{{{{tikzpicture}}}}}}}}

    \newcommand{{{{\emptyIcon}}}}{{{{%
      \hspace*{{{{5.4mm}}}}
    }}}}

    \newcommand{{{{\externalIcon}}}}{{{{%
    {LatexDocument.ICON_EXTERNAL}
    }}}}

    \newcommand{{{{\memberIcon}}}}{{{{%
    {LatexDocument.ICON_MEMBER}
    }}}}

    \newcommand{{{{\contribIcon}}}}{{{{%
    {LatexDocument.ICON_CONTRIBUTOR}
    }}}}

    \newcommand{{{{\committeeIcon}}}}{{{{%
    {LatexDocument.ICON_COMMITTEE}
    }}}}

    \newcommand{{{{\visitIcon}}}}{{{{%
    {{visit}}
    }}}}

    \newcommand{{{{\postVisitIcon}}}}{{{{%
    {{post_visit}}
    }}}}

    % ==============================================================================
    % EPFL Alumni logo
    \newcommand{{{{\epflLogo}}}}{{{{
    \begin{{{{tikzpicture}}}}[scale=0.1,draw=epflred,fill=epflred]
        % E
        \fill (0,3.15) rectangle ++(1.167,2.15) rectangle ++(2.65, -1);
        \fill (1.167, 2.15) rectangle +(2.5,1);
        \fill (3.817, 1) rectangle ++(-3.817, -1) rectangle ++(1.167, 2.15);
        % P
        \fill (4.8, 0) rectangle ++(1.167, 5.3) rectangle +(1.55, -1) (4.8, 0) ++ (1.167, 2.15) rectangle +(1.55, 1);
        \fill (7.425, 2.15) arc (-90:90:1.575) -- ++(0, -1) arc (90:-90:0.575) -- ++(0, -1) -- cycle;
        % F
        \fill (9.75, 0) rectangle ++(1.167, 2.15) rectangle +(2.45, 1);
        \fill (9.75, 3.15) rectangle ++(1.167, 2.15) rectangle +(2.7, -1);
        % L
        \fill[draw=epflred,fill=epflred] (14.4, 5.3) rectangle ++(1.167, -5.3) rectangle ++(2.65, 1);
    \end{{{{tikzpicture}}}}}}}}
    \newcommand{{{{\insertEPFLAlumniLogo}}}}{{{{%
      \begin{{{{minipage}}}}{{{{\logoWidth}}}}
        \epflLogo
      \end{{{{minipage}}}}%
    }}}}

    % ==============================================================================
    '''
)
