# EPFL Alumni Eastern Switzerland labels generator

A label generator to use when creating events from the EPFL Alumni Eastern Switzerland

## CSV data import

When reading the CSV file, the code is looking for the following column names:

| Field description      | Field name (en) | Field name (fr)       |
|------------------------|-----------------|-----------------------|
| User unique identifier | ID user AF      | ID user AF            |
| First name             | First name      | Prénom                |
| Last name              | Family Name     | Nom de famille        |
| Contribution status    | Contributor     | Cotisant/Contributeur |
| Ticket name            | Ticket name     | Nom du billet         |

NB: the matching is *case-sensitive*.

When instantiating the internal `Person` data classes, non-members (ie. external people) are detected by having an empty string for the *Contribution status* CSV field.


## Automatic detection on LaTeX setting page

When presenting the LaTeX generation options, the app tries to guess whether some settings for ticket types and whether the event has a meal/apéro after the visit. This is always overridable by the user and is based on the parsed ticket names.

The regular expression used to match against each of the ticket names are (in the order in which they are tested):

<dl>
  <dt>Meal</dt>
  <dd>looking for strings like "with meal", "with apéro", "with lunch", "avec repas", "avec souper", etc.</dd>
  <dt>Apéro</dt>
  <dd>looking for strings like "with apero", "avec apéro", etc.</dd>
</dl>

If nothing matches, the default value is used for the particular option under consideration.


### Ticket options automatic detection

If a meal or an apéro is detected based on the regular expressions, the ticket post-visit option will be checked by default.


### Event meal type automatic detection

The code assumes that an event has *either* no meal/apéro following it or an apéro or a meal, but not a combination of those options. When parsing the ticket options, if a meal is detected, then the event meal type option is set as *having a meal* by default. Same thing in case of an apéro.


## Generation of LaTeX code

Some further processing of the parsed participant data happens when generating the LaTeX code. In particular, the participation type for each participant is calculated based on the type of ticket for him/her (ie. with or without visit, with or without meal/apéro).
