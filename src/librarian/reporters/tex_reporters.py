"""This module defines the TexReporter class, which is designed to
write LaTeX reports associated with a dataset (or datasets) associated
with a catalog (or catalogs).
"""
import os
from importlib_resources import files

from librarian.actors.reporter import Reporter


# =====================================
# Local Report Templates
# =====================================

TEX_TEMPLATE_PATH = files('librarian.reporters.resources').joinpath('tex_template')
BEAMER_TEMPLATE_PATH = files('librarian.reporters.resources').joinpath('beamer_template')
TEMP_FIG_PATH = files('librarian.reporters.resources').joinpath('tempfig.png')


# =====================================
# LaTeX or Beamer Report Strings
# =====================================

def latex_figure_str(file_path=None, caption=None, label=None):
    """
    A method returning a LaTeX string for a figure.

    Parameters
    ----------
    file_path : str
        The path to the file containing the figure.
    """
    if file_path is None:
        file_path = TEMP_FIG_PATH
    if caption is None:
        caption = 'Caption text'
    if label is None:
        label = 'label'

    tex_figure = \
        "% -----------------------------------\n" + \
        "% Figure:\n" + \
        "% -----------------------------------\n" + \
        "\\begin{figure}[t!]\n" + \
        "% Figure graphics\n" + \
        "\\centering\n" + \
        "\\includegraphics[width=\\textwidth]{" + \
        f"{file_path}" + "}\n" + \
        "\n" + \
        "% Caption\n" + \
        "\\caption{\n" + \
        caption + "\n" + \
        "}\n" + \
        "\n" + \
        "% Figure Label\n" + \
        "\\label{fig:" + label + "}\n" + \
        "\\end{figure}\n" + \
        "% -----------------------------------\n\n\n"

    return tex_figure


def beamer_slide_str(file_path=None, caption=None, label=None):
    """
    A method returning a LaTeX string for a figure.

    Parameters
    ----------
    file_path : str
        The path to the file containing the figure.
    """
    if file_path is None:
        file_path = TEMP_FIG_PATH
    if caption is None:
        caption = 'Frame caption'
    if label is None:
        label = 'frame_label'

    tex_frame = \
        "% -----------------------------------\n" + \
        "% Frame:\n" + \
        "% -----------------------------------\n" + \
        "\\begin{frame}\n" + \
        "\\label{frame:" + label + "}\n" + \
        "\\centering\n" + \
        "\\includegraphics[width=\\textwidth]{" + file_path + "}\n" + \
        "% Caption\n" +  caption + "\n" + \
        "\\end{frame}\n" + \
        "% -----------------------------------\n\n\n"

    return tex_frame


# =====================================
# TeXReporter Class
# =====================================
class TexReporter(Reporter):
    """
    A base class for writing reports associated with figures in a LaTeX document.
    """
    def __init__(self, report_name=None,
                 template_folder=None,
                 documentclass=None):
        """Initialize the TexReporter object."""
        if documentclass is None or documentclass.lower() == 'article':
            self.documentclass = 'article'

            # Get the template folder if one is not given
            if template_folder is None:
                template_folder = TEX_TEMPLATE_PATH

        elif documentclass.lower() == 'beamer':
            self.documentclass = 'beamer'

            # Get the template folder if one is not given
            if template_folder is None:
                template_folder = BEAMER_TEMPLATE_PATH

        else:
            raise ValueError("documentclass must be 'article' or 'beamer'.")

        # Initialize the reporter by using the given template:
        super().__init__(report_name=report_name,
                         template_folder=template_folder)


    def report_footer(self):
        """Returns a string containing the footer for the report.
        Note that we shouldn't need to define the report header, since
        it is defined in the template.
        """
        return "\\end{document}"


    def raise_documentclass_error(self):
        """Raise an error if the documentclass is not recognized."""
        # Shouldn't get here, since initialization should have
        # raised an error if documentclass is not 'article' or 'beamer'.
        raise AssertionError("documentclass must be 'article' or 'beamer'. "
                             "This error should have been caught "
                             "during initialization and should not "
                             "be possible.")


    # ---------------------------------
    # TeX compilation
    # ---------------------------------
    def compile_report(self):
        """Compile the report."""
        os.system("pdflatex " + self.report_name)


    # ---------------------------------
    # TeX Figure
    # ---------------------------------
    def file_report_string(self, file_path, **kwargs):
        """The string generated for a report on the given file."""
        caption=self.caption(**kwargs)
        label=self.label(file_path)

        if self.documentclass == 'article':
            return latex_figure_str(file_path, caption, label)

        if self.documentclass == 'beamer':
            return beamer_slide_str(file_path, caption, label)

        return self.raise_documentclass_error()


    # ---------------------------------
    # TeX figure utilities
    # ---------------------------------
    def caption(self, **kwargs):
        """
        A method to write a caption for a figure.
        """
        if not kwargs:  # if kwargs == {}
            return ''

        if self.documentclass == 'article':
            caption = "A figure with the following properties:\n"
            for key, value in kwargs.items():
                caption += f"% {key}: {value}\n"
            return caption

        if self.documentclass == 'beamer':
            caption = "% \\begin{itemize}\n"
            for key, value in kwargs.items():
                caption += f"% \t\\item {key}: {value}\n"
            caption += "% \\end{itemize}\n"
            return caption

        return self.raise_documentclass_error()


    def label(self, file_path):
        """Returns a label for a figure."""
        # Strip the path and the extension:
        label = file_path.split('/')[-1].split('.')[0]
        return label
