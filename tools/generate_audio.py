from query.query import Query
from utils.time_utils import user_date_to_nanos
start_nanos = 1622679180000000000.000000
end_nanos = 1622680500000000000.000000

records_dir = '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/10_0/'
tfrecords_pkl = 'query/harp_intervals/10_0.pickle'

output_file = 'output.wav'
query = Query(records_dir = records_dir, tfrecords_pkl = tfrecords_pkl).get_time(start_nanos, end_nanos).to_wav(output_file)