# -- Project information -----------------------------------------------------

project = "cheb3"
copyright = "2023-2025, YanhuiJessica"
author = "YanhuiJessica"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    'sphinx.ext.napoleon',
]

intersphinx_mapping = {
    "web3": ("https://web3py.readthedocs.io/en/latest/", None),
    "hexbytes": ("https://hexbytes.readthedocs.io/en/latest/", None),
    "python": ("https://docs.python.org/3/", None),
}

templates_path = ["_templates"]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
