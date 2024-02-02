import argparse as ap
import pandas as pd
import pickle
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from utils.time_utils import user_date_to_nanos

def check_in_between_true(df, value):
    for _, row in df.iterrows():
        if row['start_time_nanos'] <= value <= row['end_time_nanos']:
            return True
    return False

def check_in_between_pred(df, value):
    for _, row in df.iterrows():
        if row['ZONE_ENTER'] <= value <= row['ZONE_EXIT']:
            return True
    return False


if __name__ == '__main__':
    parser = ap.ArgumentParser()

    parser.add_argument("--start",
                        required=True)
    parser.add_argument("--end",
                        required=True)
    parser.add_argument("--ais_data",
                        required=True)
    parser.add_argument("--output",
                        required=True)
    args = parser.parse_args()

    start = user_date_to_nanos(args.start)
    end = user_date_to_nanos(args.end)

    df = pd.read_csv('MB03_ground_truth.csv', index_col=False)
    df_hand = df.loc[(df['start_time_nanos'] > start) & (df['start_time_nanos'] < end)]
    df_pred = pd.read_csv(args.ais_data, index_col=False)

    # create 30 second samples from nanosecond intervals
    y_true = []
    y_pred = []
    tp = []
    tn = []
    fp = []
    fn = []

    curr = start
    while curr < end:
        interval = [curr, curr + 30e9]
        # check if current interval is in hand labeled
        is_gt = check_in_between_true(df_hand, interval[0]) or check_in_between_true(df_hand, interval[1])
        is_pred = check_in_between_pred(df_pred, interval[0]) or check_in_between_pred(df_pred, interval[1])

        y_true.append(1 if is_gt else 0)
        # check if current interval is in generated label
        y_pred.append(1 if is_pred else 0)
        
        if is_gt and is_pred:
            tp.append(interval)
        elif not is_gt and not is_pred:
            tn.append(interval)
        elif is_gt and not is_pred:
            fn.append(interval)
        else:
            fp.append(interval)


        curr += 30e9

    print(len(tp), len(tn), len(fn), len(fp))
    d = {}
    d['tp'] = tp
    d['tn'] = tn
    d['fn'] = fn
    d['fp'] = fp
    with open(args.output, 'wb') as f:
        pickle.dump(d, f)
    