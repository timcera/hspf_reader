"""Collection of functions for the manipulation of time series."""

from .hspf_reader import hbn, plotgen, wdm
from .toolbox_utils.src.toolbox_utils.tsutils import about as _about


def about():
    """Display version number and system information."""
    _about(__name__)


__all__ = ["about", "hbn", "plotgen", "wdm"]
