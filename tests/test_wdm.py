"""
test_wdm
----------------------------------

Tests for `hspf_reader` module.
"""

import sys

import pandas as pd
from toolbox_utils import tsutils

try:
    from cStringIO import StringIO
except:
    from io import StringIO

from unittest import TestCase

from pandas.testing import assert_frame_equal

from hspf_reader.hspf_reader import wdm


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, "utf-8")
    except:
        pass
    return out


class TestWDM(TestCase):
    def test_extract1(self):
        ret1 = wdm("tests/data.wdm", 1)
        ret1.columns = ["data.wdm_1"]
        ret2 = tsutils.asbestfreq(
            pd.read_csv("tests/data_wdm_1.csv", index_col=0, parse_dates=True)
        )
        assert_frame_equal(ret1, ret2, check_dtype=False)

    def test_extract2(self):
        ret1 = wdm("tests/data.wdm", 2)
        ret1.columns = ["data.wdm_2"]
        ret2 = tsutils.asbestfreq(
            pd.read_csv("tests/data_wdm_2.csv", index_col=0, parse_dates=True)
        )
        print(ret1)
        print(ret2)
        assert_frame_equal(ret1, ret2, check_dtype=False)
