import pytest

from utils.tfrecord_utils import *

class TestRecordWriter:
    def test_0(self):
        ...

class TestGetAudio:
    def test_0(self):
        ...
    
class TestTranslateRecordToYmd:
    def test_0(self):
        record = '1638274380000000000.000000_1638274410000000000.000000_A0_B0_C0_D0_E0_F1.tfrecord'
        print(translate_record_to_ymd(record))
        assert translate_record_to_ymd(record) == ('20211130 121300', '20211130 121330')

class TestTranslateRecordToInterval:
    def test_0(self):
        record = '1638274380000000000.000000_1638274410000000000.000000_A0_B0_C0_D0_E0_F1.tfrecord'
        assert translate_record_to_interval(record) == (1638274380000000000.000000, 1638274410000000000.000000)

class TestTranslateRecordToLabel:
    def test_0(self):
        record = '1638274380000000000.000000_1638274410000000000.000000_A0_B0_C0_D0_E0_F1.tfrecord'
        assert translate_record_to_label(record) == ('A0', 'B0', 'C0', 'D0', 'E0', 'F1')
    
class TestCreateRecordsPickle:
    def test_0(self):
        ...

