import pytest

from src.audio_fetch import AudioFetcher
from utils.time_utils import user_date_to_nanos

class TestGenerateWavSegments:
    def test_0(self):
        assert True

class TestGenerateTargetWavs:
    wav_dir = '/data/kraken/teams/acoustic_data/ais_data_labeling/wav/harp/'
    # NOTE: _generate_target_wavs is stored in AudioFetcher's self.target_wavs and self.target_wavs_filenames
    def test_0(self):
        start_nanos = user_date_to_nanos("20190201 000000")
        end_nanos = user_date_to_nanos("20190301 0000000")
        af = AudioFetcher(interval=[start_nanos, end_nanos], wav_dir=self.wav_dir)
        assert af.target_wavs_filenames[0] == self.wav_dir + 'harp_20190201000000.x.wav'
        assert af.target_wavs_filenames[-1] == self.wav_dir + 'harp_20190228230000.x.wav'

    def test_1(self):
        start_nanos = user_date_to_nanos("20200601 000000")
        end_nanos = user_date_to_nanos("20200701 000000")
        af = AudioFetcher(interval=[start_nanos, end_nanos], wav_dir=self.wav_dir)
        assert af.target_wavs_filenames[0] == self.wav_dir + 'harp_20200531230500.x.wav'
        assert af.target_wavs_filenames[-1] == self.wav_dir + 'harp_20200630230500.x.wav' 

    def test_invalid_interval(self):
        with pytest.raises(Exception) as info:
            af = AudioFetcher(interval=[user_date_to_nanos("20200701 000000"), user_date_to_nanos("20200601 000000")], wav_dir=self.wav_dir)

        assert str(info.value) == "Not a valid interval"
    

class TestCreateSegmentWav:
    def test_0(self):
        assert True



    
