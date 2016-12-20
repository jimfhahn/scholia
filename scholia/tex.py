r"""tex.

Usage:
  scholia.tex extract-qs-from-aux <file>
  scholia.tex write-bbl-from-aux <file>
  scholia.tex write-bib-from-aux <file>

Description:
  Work with latex and bibtex.

  The functionality is not complete.


Example latex document:

\documentclass{article}
\pdfoutput=1
\usepackage[utf8]{inputenc}

\begin{document}
Scientific citations \cite{Q26857876,Q21172284}.
Semantic relatedness \cite{Q26973018}.
\bibliographystyle{unsrt}
\bibliography{}
\end{document}

"""


from __future__ import print_function

from os.path import splitext

import re

from .api import (entity_to_authors, entity_to_month, entity_to_title,
                  entity_to_year, wb_get_entities)


def extract_qs_from_aux_string(string):
    r"""Extract qs from string.

    Paramaters
    ----------
    string : str
        Extract Wikidata identifiers from citations.

    Returns
    -------
    qs : list of str
        List of strings.

    Examples
    --------
    >>> string = "\citation{Q28042913}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913']

    >>> string = "\citation{Q28042913,Q27615040}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913', 'Q27615040']

    >>> string = "\citation{Q28042913,Q27615040,Q27615040}"
    >>> extract_qs_from_aux_string(string)
    ['Q28042913', 'Q27615040', 'Q27615040']

    """
    matches = re.findall(r'^\\citation{(Q\d+?(?:,Q\d+?)*)}', string,
                         flags=re.MULTILINE | re.UNICODE)
    qs = [q for submatches in matches for q in submatches.split(',')]
    return qs


def main():
    """Handle command-line arguments."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['extract-qs-from-aux']:
        string = open(arguments['<file>']).read()
        print(" ".join(extract_qs_from_aux_string(string)))

    elif arguments['write-bbl-from-aux']:
        aux_filename = arguments['<file>']
        base_filename, _ = splitext(aux_filename)
        bbl_filename = base_filename + '.bbl'

        string = open(aux_filename).read()
        qs = extract_qs_from_aux_string(string)
        entities = wb_get_entities(qs)

        widest_label = max([len(q) for q in qs])
        bbl = u'\\begin{thebibliography}{%d}\n\n' % widest_label

        for q in qs:
            entity = entities[q]
            bbl += '\\bibitem{%s}\n' % q
            bbl += u", ".join(entity_to_authors(entity)) + '.\n'
            bbl += entity_to_title(entity) + '.\n'

            bbl += '\n'

        bbl += '\\end{thebibliography}\n'

        with open(bbl_filename, 'w') as f:
            f.write(bbl.encode('utf-8'))

        with open(aux_filename, 'a') as f:
            for n, q in enumerate(qs, 1):
                f.write('\\bibcite{%s}{%d}\n' % (q, n))

    elif arguments['write-bib-from-aux']:
        aux_filename = arguments['<file>']
        base_filename, _ = splitext(aux_filename)
        bib_filename = base_filename + '.bib'

        string = open(aux_filename).read()
        qs = extract_qs_from_aux_string(string)
        entities = wb_get_entities(qs)

        bib = ""
        for q in qs:
            entity = entities[q]
            bib += "@Article{%s,\n" % q
            bib += "  author = {%s},\n" % \
                   u" and ".join(entity_to_authors(entity))
            bib += "  title =  {%s},\n" % entity_to_title(entity)
            bib += "  year =   {%s},\n" % entity_to_year(entity)
            bib += "  month =  {%s},\n" % entity_to_month(entity)
            bib += '}\n\n'

        with open(bib_filename, 'w') as f:
            f.write(bib.encode('utf-8'))


if __name__ == '__main__':
    main()