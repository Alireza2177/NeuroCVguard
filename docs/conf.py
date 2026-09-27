"""Offline Sphinx/MyST documentation; no network or source-path injection."""

from neurocvguard import __version__

project = "NeuroCVguard"
release = __version__
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon"]
napoleon_use_param = False
napoleon_use_rtype = False
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
exclude_patterns = ["_build"]
html_theme = "alabaster"
html_show_copyright = False
autodoc_typehints = "none"
autodoc_member_order = "bysource"
nitpicky = True
myst_heading_anchors = 3
