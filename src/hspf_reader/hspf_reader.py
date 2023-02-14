"""Collection of functions for reading different time series from HSPF."""

import os.path as _os_path
import sys as _sys
import warnings as _warnings

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter
from toolbox_utils import tsutils
from toolbox_utils.readers.hbn import hbn_extract as _hbn
from toolbox_utils.readers.plotgen import plotgen_extract as _plotgen
from toolbox_utils.readers.wdm import wdm_extract as _wdm

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
    *plotgen_args : str
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
    return tsutils.printiso(
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
    *wdmpath : str
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
    return tsutils.printiso(wdm(*wdmpath, start_date=start_date, end_date=end_date))


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


@cltoolbox.command("hbn", formatter_class=RSTHelpFormatter)
def _hbn_cli(
    hbnfilename, interval, start_date=None, end_date=None, sort_columns=False, *labels
):
    r"""Prints out data to the screen from a HSPF binary output file.

    Parameters
    ----------
    hbnfilename : str
        The HSPF binary output file.  This file must have been created from
        a completed model run.

    interval : str
        One of 'yearly', 'monthly', 'daily', or 'bivl'.  The 'bivl' option is
        a sub-daily interval defined in the UCI file.  Typically 'bivl' is used
        for hourly output, but can be set to any value that evenly divides into
        a day.

    *labels : str
        The remaining arguments uniquely identify a time-series in the
        binary file.  The format is 'OPERATIONTYPE,ID,VARIABLEGROUP,VARIABLE'.

        For example: 'PERLND,101,PWATER,UZS IMPLND,101,IWATER,RETS'

        Leaving a section without an entry will wild card that
        specification.  To get all the PWATER variables for PERLND 101 the
        label would read:

        'PERLND,101,PWATER,'

        To get TAET for all PERLNDs:

        'PERLND,,,TAET'

        Note that there are spaces ONLY between label specifications not within
        the labels themselves.

        OPERATIONTYE can be PERLND, IMPLND, RCHRES, and BMPRAC.

        ID is the operation type identification number specified in the UCI
        file. These numbers must be in the range 1-999.

        Here, the user can specify

            - a single ID number to match
            - no entry, matching any operation ID number
            - a range, specified as any combination of simple integers and
              groups of integers marked as "start:end", with multiple allowed
              sub-ranges separated by the "+" sign.

        Examples:

            +-----------------------+-------------------------------+
            | Label ID              | Expands to:                   |
            +=======================+===============================+
            | 1:10                  | 1,2,3,4,5,6,7,8,9,10          |
            +-----------------------+-------------------------------+
            | 101:119+221:239       | 101,102..119,221,221,...239   |
            +-----------------------+-------------------------------+
            | 3:5+7                 | 3,4,5,7                       |
            +-----------------------+-------------------------------+

        VARIABLEGROUP depends on OPERATIONTYPE where::

            if OPERATIONTYPE is PERLND then VARIABLEGROUP can be one of
                'ATEMP', 'SNOW', 'PWATER', 'SEDMNT', 'PSTEMP', 'PWTGAS',
                'PQUAL', 'MSTLAY', 'PEST', 'NITR', 'PHOS', 'TRACER'

            if OPERATIONTYPE is IMPLND then VARIABLEGROUP can be one of
                'ATEMP', 'SNOW', 'IWATER', 'SOLIDS', 'IWTGAS', 'IQUAL'

            if OPERATIONTYPE is RCHRES then VARIABLEGROUP can be one of
                'HYDR', 'CONS', 'HTRCH', 'SEDTRN', 'GQUAL', 'OXRX', 'NUTRX',
                'PLANK', 'PHCARB', 'INFLOW', 'OFLOW', 'ROFLOW'

            if OPERATIONTYPE is BMPRAC then VARIABLEGROUP is not used and you
            have to leave VARIABLEGROUP as a wild card.  For example,
            'BMPRAC,875,,RMVOL'.

        The Time Series Catalog in the HSPF Manual lists all of the variables
        in each of these VARIABLEGROUPs.  For BMPRAC, all of the variables in
        all Groups in the Catalog are available in the unnamed (blank) Group.

    ${start_date}

    ${end_date}

    sort_columns:
        [optional, default is False]

        If set to False will maintain the columns order of the labels.  If set
        to True will sort all columns by their columns names."""
    tsutils.printiso(
        hbn(
            hbnfilename,
            interval,
            *labels,
            start_date=start_date,
            end_date=end_date,
            sort_columns=sort_columns,
        )
    )


@tsutils.copy_doc(_hbn_cli)
def hbn(hbnpath, interval, *labels, **kwds):
    """Read hbn file and return a pandas DataFrame."""

    try:
        start_date = kwds.pop("start_date")
    except KeyError:
        start_date = None
    try:
        end_date = kwds.pop("end_date")
    except KeyError:
        end_date = None
    try:
        sort_columns = kwds.pop("sort_columns")
    except KeyError:
        sort_columns = False
    if len(kwds) > 0:
        raise ValueError(
            tsutils.error_wrapper(
                f"""
                The only allowed keywords are start_date and end_date.  You
                have given {kwds}.
                """
            )
        )

    labels = tsutils.make_list(labels)

    result = pd.DataFrame()
    for lab in [labels]:
        nts = _hbn(hbnpath, interval, lab, sort_columns=sort_columns)
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
