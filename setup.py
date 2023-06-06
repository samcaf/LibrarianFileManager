import setuptools

setuptools.setup(
    name="LibrarianFileManager",
    version="1.0.2",
    author="Samuel Alipour-fard",
    author_email="samuelaf@mit.edu",
    description="A librarian for managing your files.",
    long_description="General purpose file management tools for initializing, keeping track of, and interacting with file structures (e.g. for cataloging data, plotting of figures, etc.).",
    long_description_content_type="text",
    url="https://github.com/samcaf/LibrarianFileManager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
