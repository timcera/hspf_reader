# -*- coding: utf-8 -*-
"""Collection of functions for reading different time series from HSPF."""

import os.path as _os_path
import sys as _sys
import warnings as _warnings

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter
from toolbox_utils import tsutils

from .functions import hbn
from .functions.plotgen import plotgen as _plotgen
from .functions.wdm import wdm as _wdm

_warnings.filterwarnings("ignore")


@cltoolbox.command()
def about():
    """Display version number and system information."""
    tsutils.about(__name__)


@cltoolbox.command("plotgen", formatter_class=RSTHelpFormatter)
def _plotgen_cli(start_date=None, end_date=None, *plotgen_args):
    """Print out plotgen data to the screen with ISO-8601 dates.

    Parameters
    ----------
    plotgen_args : str
        Path and plotgen file name
        followed by space separated list of
        fields. For example::

            'file.plt 234 345 456'

            OR
            `file.plt` can be space separated sets of 'plotgetpath,field'.

            'file.plt,FIELD1 file2.plt,FIELD2 file.plt,FIELD3'
    ${start_date}
    ${end_date}

    """
    return tsutils._printiso(
        plotgen(*plotgen_args, start_date=start_date, end_date=end_date)
    )


@tsutils.copy_doc(_plotgen_cli)
def plotgen(*plotgenpath, **kwds):
    """Read plotgen file and return a pandas DataFrame."""

    try:
        start_date = kwds.pop("start_date")
    except KeyError:
        start_date = None
    try:
        end_date = kwds.pop("end_date")
    except KeyError:
        end_date = None
    if len(kwds) > 0:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                The only allowed keywords are start_date and end_date.  You
                have given {kwds}.
                """
            )
        )

    labels = tsutils.normalize_command_line_args(plotgenpath)

    result = pd.DataFrame()
    cnt = 0
    for lab in labels:
        pltpath, *fields = lab
        if fields:
            for field in fields:
                nts = _plotgen(pltpath)[field]
                col_name = f"{_os_path.basename(pltpath)}_{field}"
                if col_name in result.columns:
                    cnt = cnt + 1
                    col_name = f"{col_name}_{cnt}"
                nts.columns = [col_name]
                result = result.join(nts, how="outer")
        else:
            result = _plotgen(pltpath)
        result = tsutils.common_kwds(result, start_date=start_date, end_date=end_date)
    return tsutils.asbestfreq(result)


@cltoolbox.command("wdm", formatter_class=RSTHelpFormatter)
def _wdm_cli(start_date=None, end_date=None, *wdmpath):
    """Print out DSN data to the screen with ISO-8601 dates.

    Parameters
    ----------
    wdmpath : str
        Path and WDM file name
        followed by space separated list of
        DSNs. For example::

            'file.wdm 234 345 456'

            OR
            `wdmpath` can be space separated sets of 'wdmpath,dsn'.

            'file.wdm,101 file2.wdm,104 file.wdm,227'
    ${start_date}
    ${end_date}

    """
    return tsutils._printiso(wdm(*wdmpath, start_date=start_date, end_date=end_date))


@tsutils.copy_doc(_wdm_cli)
def wdm(*wdmpath, **kwds):
    """Read WDM file and return a pandas DataFrame."""

    try:
        start_date = kwds.pop("start_date")
    except KeyError:
        start_date = None
    try:
        end_date = kwds.pop("end_date")
    except KeyError:
        end_date = None
    if len(kwds) > 0:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                The only allowed keywords are start_date and end_date.  You
                have given {kwds}.
                """
            )
        )

    labels = tsutils.make_list(wdmpath)

    result = pd.DataFrame()
    cnt = 0
    for lab in [labels]:
        wdmname, *dsns = lab
        for dsn in dsns:
            nts = _wdm(wdmname, int(dsn))
            col_name = f"{_os_path.basename(wdmname)}_{dsn}"
            if col_name in result.columns:
                cnt = cnt + 1
                col_name = f"{nts.columns[0]}_{cnt}"
            nts.columns = [col_name]
            result = result.join(nts, how="outer")
    result = tsutils.common_kwds(result, start_date=start_date, end_date=end_date)
    return tsutils.asbestfreq(result)


def main():
    """Set debug and run cltoolbox.main function."""
    if not _os_path.exists("debug_hspf_reader"):
        _sys.tracebacklimit = 0
    cltoolbox.main()


if __name__ == "__main__":
    main()
