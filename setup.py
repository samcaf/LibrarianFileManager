import setuptools

setuptools.setup(
    name="LibrarianFileManager",
    author="Samuel Alipour-fard",
    author_email="samuelaf@mit.edu",
    description="A librarian for managing your files: "\
        "General purpose file management tools for initializing, "\
        "keeping track of, and interacting with file structures "\
        "(e.g. for cataloging data, plotting of figures, etc.).",
    url="https://github.com/samcaf/LibrarianFileManager",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
