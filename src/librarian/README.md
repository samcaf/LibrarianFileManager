# TODO:

## Basic
    * Associate TypedDicts with catalogs
        * How do I store these in the yaml file?
        * How can I make it okay for users to not include this info, and easy for them to include it if they want to
    * Enable support for adding parameters for typed dicts
        * When turning params (dict of str -> str) from the yaml into dicts, start with a default set of params and then use TypedDict.update method to turn it into something with actual types (dict of str -> predefined type)
        * If you want to add additional params to the typed dict, just give a default associated with all of the data that has already been generated

## Specific
    * EWOC project librarian;
    * File converter;
    * Different HEP readers (lhe, hepmc, etc).
