"""This module defines the abstract Reporter class, which is designed to
write reports associated with a dataset (or datasets) associated
with a catalog (or catalogs).
"""
import os
from datetime import datetime
import shutil
from pathlib import Path

from librarian.actor import Actor


class Reporter(Actor):
    """
    A class for writing data to files and storing the filenames in a catalog.

    This class provides methods to write data to files in various formats
    such as pickled files, NumPy files, and plain text files. It also supports
    adding the file paths to an associated catalog.

    Parameters
    ----------
    default_extension : str, optional
        The default file extension to use when writing files. Supported
        extensions are '.pkl', '.npz', '.npy', '.txt', and None.
        If None, the extension needs to be explicitly provided
        when writing a file. Default is None.

    Attributes
    ----------
    default_extension : str or None
        The default file extension to use when writing files.
    """

    def __init__(self, report_name=None,
                 template_folder=None,
                 new_report=False):
        """Initialize the Reporter."""
        if report_name is None:
            report_name = "report"
            report_name += "-" + str(datetime.now().time()
                                     ).replace(":", "-").replace(".", "-")

        # Making folder for the .tex file
        self.folder = report_name
        self.report_loc = self.folder + "/report.tex"

        new_report = new_report or not Path(self.report_loc).exists()

        if new_report:
            if not Path(self.report_loc).exists():
                # If the report did not already exist, initialize it
                Path(self.folder).mkdir(parents=True, exist_ok=True)
            if template_folder is None:
                # If no template folder was provided, use the default
                template_folder = "beamer_template"

            if os.path.exists(self.folder):
                # If the report folder already exists, delete it
                shutil.rmtree(self.folder)

            # Copying the template folder to the report folder
            shutil.copytree(template_folder, self.folder)

            # If we have a template, we can copy it over
            # without having to re-write the header and footer
            # Writing the header
            # self.write_header()
            # self.write_footer()


    # =====================================
    # Utilities
    # =====================================
    # ---------------------------------
    # Header and footer
    # ---------------------------------
    def report_header(self, **kwargs):
        """Write the header for the report."""
        raise NotImplementedError("report_header() not implemented.")

    def report_footer(self):
        """Write the footer for the report."""
        raise NotImplementedError("report_footer() not implemented.")


    def write_header(self, **kwargs):
        """Write the header for the report."""
        with open(self.report_loc, 'w', encoding='utf-8') as report:
            report.write("% HEADER\n")
            report.write(self.report_header(**kwargs))
            report.write("\n% END HEADER\n\n")

    def write_footer(self):
        """Close the report."""
        with open(self.report_loc, 'a', encoding='utf-8') as report:
            report.write("% FOOTER\n")
            report.write(self.report_footer())
            report.write("\n% END FOOTER")

    def remove_footer(self):
        """Remove the footer from the report."""
        with open(self.report_loc, "r+", encoding='utf-8') as report:
            # Don't need tell to seek back to start of file if first line matches
            cookie = 0
            while line := report.readline():
                if '% FOOTER' in line:
                    # Revert to position before we read in most recent line
                    report.seek(cookie)
                    report.truncate()
                    break
                # Save off position cookie prior to reading next line
                cookie = report.tell()


    # =====================================
    # File Specific
    # =====================================
    def file_report_string(self, file_path, **kwargs):
        """The string generated for a report on the given file."""
        raise NotImplementedError("file_report_string() not implemented.")


    def file_action(self, file_path, **kwargs):
        """Writes a report associated with a particular file.
        Note that this does not delete and then re-write the footer,
        so this should be used in conjunction with remove_footer(),
        as in the catalog-specific methods below

        Parameters
        ----------
        file_path : str
            The path to the file containing the figure.
        """
        rewrite_footer = kwargs.pop('rewrite_footer', True)

        if rewrite_footer:
            self.remove_footer()

        with open(self.report_loc, 'a', encoding='utf-8') as report:
            report_string = self.file_report_string(file_path, **kwargs)
            report.write(report_string)

        if rewrite_footer:
            self.write_footer()


    # =====================================
    # Catalog Specific
    # =====================================
    def report_data_from_catalog(self, catalog, data_label, params, **kwargs):
        """Write a report on a given file in a catalog."""
        file_path = catalog.get_filename(data_label, params)
        params.update({'data_label': data_label})
        kwargs.update(params)

        self.file_action(file_path, **kwargs)


    def act_on_catalog(self, catalog, **kwargs):
        """Write a report on all files within a catalog."""
        self.remove_footer()

        for data_label, params in catalog.get_data_label_params():
            file_path = catalog.get_filename(data_label, params)
            # Setting up parameters for this file
            params.update({'data_label': data_label})
            data_kwargs = kwargs.copy()
            data_kwargs.update(params)
            # Not re-writing footer at each intermediate step
            data_kwargs.update({'rewrite_footer': False})
            # Writing the report for this file
            self.file_action(file_path, **kwargs)

        self.write_footer(**kwargs)
