import pytest

from utils.time_utils import *

class TestUserDateToNanos:
    def test_0(self):
        assert user_date_to_nanos("20200101 000000") == 1577836800000000000

class TestUSCGDateToNanos:
    def test_0(self):
        assert uscg_date_to_nanos('2018-11-01T00:00:02') == 1541030402000000000


class TestUSCGAISToNanos:
    def test_0(self):
        assert uscg_ais_to_nanos('USCG_AIS_5min_MB_2021-01.csv') == 1609459200000000000


class TestMarineCadastreToNanos:
    def test_0(self):
        assert marine_cadastre_to_nanos("2019-09.csv") == 1567296000000000000

class TestWavStrToNanos:
    def test_0(self):
        assert wav_str_to_nanos("20181114034650") == 1542167210000000000

class TestUTCToNanos:
    def test_0(self):
        assert utc_to_nanos("2018-11-14T03:46:50.000Z") == 1542167210000000000


class TestNanosToYmdStr:
    def test_0(self):
        assert nanos_to_ymd_str(1542167210000000000) == "20181114 034650"
