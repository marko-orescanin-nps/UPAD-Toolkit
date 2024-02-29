import pandas as pd
import sklearn.metrics as metrics

def get_location_dict(df, full_loc_dict, index_start, index_end):
    examples = df['unique_id'][index_start:index_end]
    location_dict = [(id, full_loc_dict[id]) for id in examples]
    return location_dict

def SingleExponential(pred, alpha):
    x = pred[0]
    filtered_preds = []
    
    for i in range(1, len(pred)):
        filtered_preds.append(x)
        x = alpha*pred[i] + (1-alpha)*x

    filtered_preds.append(x)

    return filtered_preds

def DoubleExponential(pred, alpha, beta):
    x = pred[0]
    b = pred[1] - pred[0]

    filtered_preds = []
    filtered_preds.append(pred[0])
    filtered_preds.append(pred[1])

    for i in range(2, len(pred)):
        x_prev = x
        x = alpha * pred[i] + (1-alpha)*(x+b)
        b = beta*(x - x_prev) + (1-beta)*b
        
        filtered_preds.append(x+b)
        
    return filtered_preds

def uncertainty_plot(aleatoric, epistemic, entropy, y_pred, y_true, metric=accuracy_score):
    if metric == accuracy_score:
        metric_label = 'Test Accuracy'
    elif metric == metrics.f1_score:
        metric_label = 'Test F1'
    elif metric == metrics.recall_score:
        metric_label = 'Recall'
    elif metric == metrics.precision_score:
        metric_label = 'Precision'
    elif metric == metrics.matthews_corrcoef:
        metric_label = 'Matthews Correlation Coeff'
    else:
        print("Metric Not Implemented")
        return

    acc_cal_aleatoric = []
    acc_cal_epistemic = []
    acc_cal_entropy = []
    
    one_pct = int(y_true.shape[0] * .01)

    pred_labels_sort_aleatoric = [v for _,v in sorted(zip(aleatoric,y_pred), key = lambda x: x[0], reverse=True)]
    true_labels_sort_aleatoric = [v for _,v in sorted(zip(aleatoric,y_true), key = lambda x: x[0], reverse=True)]

    pred_labels_sort_epistemic = [v for _,v in sorted(zip(epistemic,y_pred), key = lambda x: x[0], reverse=True)]
    true_labels_sort_epistemic = [v for _,v in sorted(zip(epistemic,y_true), key = lambda x: x[0], reverse=True)]

    pred_labels_sort_entropy = [v for _,v in sorted(zip(entropy,y_pred), key = lambda x: x[0], reverse=True)]
    true_labels_sort_entropy = [v for _,v in sorted(zip(entropy,y_true), key = lambda x: x[0], reverse=True)]
    
    for p in range(100):
        tl_aleatoric = true_labels_sort_aleatoric[p*one_pct:]
        pl_aleatoric = pred_labels_sort_aleatoric[p*one_pct:]

        tl_epistemic = true_labels_sort_epistemic[p*one_pct:]
        pl_epistemic = pred_labels_sort_epistemic[p*one_pct:]

        tl_entropy = true_labels_sort_entropy[p*one_pct:]
        pl_entropy = pred_labels_sort_entropy[p*one_pct:]
        
        if not metric in [metrics.matthews_corrcoef, metrics.accuracy_score]:
            accuracy_aleatoric=metric(tl_aleatoric,pl_aleatoric, zero_division=1.0)
            accuracy_epistemic=metric(tl_epistemic,pl_epistemic, zero_division=1.0)
            accuracy_entropy=metric(tl_entropy,pl_entropy, zero_division=1.0)
        else:
            accuracy_aleatoric=metric(tl_aleatoric,pl_aleatoric)
            accuracy_epistemic=metric(tl_epistemic,pl_epistemic)
            accuracy_entropy=metric(tl_entropy,pl_entropy)
        acc_cal_aleatoric.append(accuracy_aleatoric)
        acc_cal_epistemic.append(accuracy_epistemic)
        acc_cal_entropy.append(accuracy_entropy)

    acc_cal_aleatoric.reverse()
    acc_cal_epistemic.reverse()
    acc_cal_entropy.reverse()
    
    
    rc('font',**{'family':'sans-serif','sans-serif':['DejaVu Sans'],'size':10})
    
    rc('mathtext',**{'default':'regular'})
    plt.rcParams['font.size'] = 18
    plt.rcParams['axes.linewidth'] = 1
    
    x_vals = list(range(100))
    
    figure = plt.figure(figsize=([10,7]))

    plt.ylabel(metric_label, fontsize=22)
    plt.xlabel(f"Ratio of Data Retained")
    plt.title(f"{metric_label} vs Ratio of Data Retained")
    
    plt.plot(x_vals[10:],acc_cal_aleatoric[10:], linewidth=3, c='r', linestyle='--')
    plt.plot(x_vals[10:], acc_cal_epistemic[10:], linewidth=3, c='g', linestyle='-.')
    plt.plot(x_vals[10:],acc_cal_entropy[10:], linewidth=3, c='b', linestyle='-')

    plt.legend(['Aleatoric', 'Epistemic', 'Entropy'], loc='lower left')
    figure.tight_layout()
    
    plt.show()
    plt.close()

    return acc_cal_aleatoric, acc_cal_epistemic, acc_cal_entropy, x_vals

def load_inference_data(inference_data) -> pd.DataFrame:
    with open(inference_data, 'rb') as f:
        test = pickle.load(f)

    t_sorted = sorted(zip(test['unique_id'],test['preds'], test['mean_pred'], test['multilabel'],test['variance'],test['label'], test['epistemic_dep'], test['aleatoric_dep'],test['entropy'] ),key = lambda x: x[0])
    unique_id, preds, mean_preds, multilabel, variance, label, epistemic, aleatoric, entropy = zip(*t_sorted)
    # acc_cal_aleatoric, acc_cal_epistemic, acc_cal_entropy, x_vals = uncertainty_plot(aleatoric, epistemic, entropy, preds, np.array(label))
    pred_quality = [1 if a == b else 0 for a,b in zip(preds,label)]
    var_min = np.min(variance)
    var_max = np.max(variance)
    epistemic_min = np.min(epistemic)
    epistemic_max = np.max(epistemic)
    cmap = matplotlib.colors.ListedColormap(['orangered', 'lawngreen'])
    data = pd.DataFrame(list(zip(unique_id, preds, filtered_preds_SE, pred_quality, variance, epistemic)), columns = ['unique_id', 'preds', 'filtered_preds', 'pred_quality', 'variance','epistemic'])
    return data 

def plot_model_predictions(inference_data, output_img, start_index, end_index):
    '''
    :inference_data: pickle file containing inference data
    :output_img: path to output image file to
    '''

    data = load_inference_data(inference_data).iloc[start_index:end_index]
    for i in range(0,len(data), 150):
        size = 150
        data_slice=data.iloc[i:i+150]

        if data_slice.shape[0] != 150:
            size=data_slice.shape[0]
            
        fig,ax1a = plt.subplots(figsize=(20,4))
        ax1a.set_xlim(i-1,i+size+1)
        ax1a.set_ylim(-0.5,1.5)
        ax1a.set_yticks((0,1))
        ax1a.set_yticklabels(['No Ship', 'Ship'])
        ax1a.set_xlabel('Index of 30-Second Sample')
        
        
        sns.lineplot(data=data_slice, x='unique_id', y='preds',color='black',zorder=2,ax=ax1a)
        sns.scatterplot(data=data_slice, x='unique_id', y='preds', hue='pred_quality', palette={0:'orangered',1:'lawngreen'},s=40,zorder=10,legend='full',ax=ax1a)
        sns.scatterplot(data=data_slice, x='unique_id', y='filtered_preds', color='k', s = 8, zorder=15, ax=ax1a)
        ax1b = ax1a.twinx()
        
        
        sns.barplot(data=data_slice,x='unique_id',y='epistemic', color='gray',alpha=0.3,zorder=1,ax=ax1b)
        ax1b.set_ylim(epistemic_min,epistemic_max)
        ax1b.set_ylabel('Uncertainty - Epistemic')
        
        ax1a.set_xticklabels(labels=range(i,i+size,1),rotation=90,fontsize=8)
        
        
        correct_pred = matplotlib.lines.Line2D([], [], color="lawngreen", marker='o', markerfacecolor="lawngreen")
        incorrect_pred = matplotlib.lines.Line2D([], [], color="orangered", marker='o', markerfacecolor="orangered")
        
        ax1a.legend(handles=[correct_pred, incorrect_pred],labels=['Correct Pred','Incorrect Pred'],loc='best')
        
        ax1b.zorder = 1
        ax1a.zorder = 2
        ax1a.patch.set_visible(False)
        ax1a.set_ylabel(None)
        
        plt.show()
        plt.savefig(output_img, dpi=300)
        plt.close()

        