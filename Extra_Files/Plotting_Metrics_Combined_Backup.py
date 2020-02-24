import os, time, argparse, sys, glob
import argparse
import glob
import os
import sys
import time
from copy import deepcopy
from functools import reduce

import matplotlib.pyplot as plt
import numpy as np

import utils as eutils

plt.style.use('ggplot')
plt.rcParams.update({'font.size': 12, 'font.weight':'bold'})
plt.rc("font", family="sans-serif")


def get_arguments():
    # Initialize the parser
    parser = argparse.ArgumentParser(description='Paramters for sensitivity analysis of heatmaps')

    parser.add_argument('-idp', '--input_dir_path', help='Path of the input directory', metavar='DIR')

    parser.add_argument('-op', '--out_path',
                        help='Path of the output directory where you want to save the results (Default is ./)')

    parser.add_argument('-mn', '--method_name', choices=['occlusion', 'ig', 'sg', 'grad', 'lime', 'mp', 'inpgrad'],
                        help='Method you are analysing')

    # parser.add_argument('--exp_num', type=int,
    #                     help='Experiment index for a particular method.Default=0', default=0)

    # parser.add_argument('--metric_name', choices=['ssim', 'spearman', 'hog', 'insertion', 'deletion', 'iou'],
    #                     help='Metric to be computed')

    parser.add_argument('--save', action='store_true', default=False,
                        help=f'Flag to say that plot need to be saveed. '
                             f'Default=False')

    # Parse the arguments
    args = parser.parse_args()
    # args.start_idx = 0
    # args.end_idx = 2000

    # if args.num_variations is None:
    #     print('Please provide this number.\nExiting')
    #     sys.exit(0)
    # elif args.num_variations < 2:
    #     print('This number cant be less than 2.\nExiting')
    #     sys.exit(0)

    if args.input_dir_path is None:
        print('Please provide image dir path. Exiting')
        sys.exit(1)
    args.input_dir_path = os.path.abspath(args.input_dir_path)

    if args.method_name is None:
        print('Please provide the name of the method.\nExiting')
        sys.exit(0)

    # if args.metric_name is None:
    #     print('Please provide the name of the metric.\nExiting')
    #     sys.exit(0)

    if args.out_path is None:
        args.out_path = './'
    args.out_path = os.path.abspath(args.out_path)

    return args


########################################################################################################################
def combined_errorbar_plot(data_dicts, fName, out_dir, title=None, save=False):
    width = 0.6
    alpha = 1
    fig, ax = plt.subplots(figsize=(10, 6))
    eBar_color = 'dimgrey'
    err_kwargs = dict(elinewidth=1, capsize=0, markeredgewidth=0, ecolor=eBar_color)
    bar_colors = ['tomato', 'cornflowerblue', 'mediumseagreen']

    #################################################
    ## SSIM DATA
    ssim_mean_data = (np.mean(data_dicts['ssim']['mean_dict']['googlenet']),
                      np.mean(data_dicts['ssim']['mean_dict']['pytorch']),
                      np.mean(data_dicts['ssim']['mean_dict']['madry'])
                      )

    ssim_var_data = (np.sqrt(np.mean(data_dicts['ssim']['var_dict']['googlenet'])),
                     np.sqrt(np.mean(data_dicts['ssim']['var_dict']['pytorch'])),
                     np.sqrt(np.mean(data_dicts['ssim']['var_dict']['madry']))
                     )

    ## SPEARMAN DATA
    spearman_mean_data = (np.mean(data_dicts['spearman']['mean_dict']['googlenet']),
                      np.mean(data_dicts['spearman']['mean_dict']['pytorch']),
                      np.mean(data_dicts['spearman']['mean_dict']['madry'])
                      )

    spearman_var_data = (np.sqrt(np.mean(data_dicts['spearman']['var_dict']['googlenet'])),
                     np.sqrt(np.mean(data_dicts['spearman']['var_dict']['pytorch'])),
                     np.sqrt(np.mean(data_dicts['spearman']['var_dict']['madry']))
                     )

    ## HOG DATA
    hog_mean_data = (np.mean(data_dicts['hog']['mean_dict']['googlenet']),
                      np.mean(data_dicts['hog']['mean_dict']['pytorch']),
                      np.mean(data_dicts['hog']['mean_dict']['madry'])
                      )

    hog_var_data = (np.sqrt(np.mean(data_dicts['hog']['var_dict']['googlenet'])),
                     np.sqrt(np.mean(data_dicts['hog']['var_dict']['pytorch'])),
                     np.sqrt(np.mean(data_dicts['hog']['var_dict']['madry']))
                     )
    #################################################

    ##GOOGLENET (Above Centre)
    rects0 = ax.barh(3 * np.arange(3) + 0.7, (ssim_mean_data[0], spearman_mean_data[0], hog_mean_data[0]),
                     height=width, alpha=alpha, color=3*[bar_colors[0]], align='center',
                     xerr=(ssim_var_data[0], spearman_var_data[0], hog_var_data[0]),
                     error_kw=err_kwargs, label='GoogleNet')

    ##PYTORCH (Centre)
    rects1 = ax.barh(3 * np.arange(3), (ssim_mean_data[1], spearman_mean_data[1], hog_mean_data[1]),
                     height=width, alpha=alpha, color=3*[bar_colors[1]], align='center',
                     xerr=(ssim_var_data[1], spearman_var_data[1], hog_var_data[1]),
                     error_kw=err_kwargs, label='ResNet50')

    ##MADRY (Below Centre)
    rects2 = ax.barh(3 * np.arange(3) - 0.7, (ssim_mean_data[2], spearman_mean_data[2], hog_mean_data[2]),
                     height=width, alpha=alpha, color=3*[bar_colors[2]], align='center',
                     xerr=(ssim_var_data[2], spearman_var_data[2], hog_var_data[2]),
                     error_kw=err_kwargs, label='MadryNet',)

    ax.set_yticks(3*np.arange(3), minor=False)
    ax.set_yticklabels(('SSIM', 'Spearman', 'HOG'), minor=False)

    if title is not None:
        ax.set_title(title, fontweight='bold', fontsize=13)
    ax.set_xticks(np.arange(0, 1.01, 0.1))

    ## (x, y, width, height)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1), ncol=3, prop={'weight':'normal'})

    # plt.legend(rects0, ['GoogleNet', 'ResNet50', 'MadryNet'])

    if args.save:
        print(f'Saving file: {os.path.join(out_dir, fName)}')
        eutils.mkdir_p(out_dir)
        fig.savefig(os.path.join(out_dir, fName), bbox_inches='tight')
        plt.close(fig)
    else:
        plt.show()
        plt.close(fig)


########################################################################################################################
if __name__ == '__main__':

    s_time = time.time()
    f_time = ''.join(str(s_time).split('.'))
    args = get_arguments()
    im_label_map = eutils.imagenet_label_mappings()

    model_names = []
    model_names.append('googlenet')
    model_names.append('pytorch')
    model_names.append('madry') #Robust_ResNet

    method_dict = {'grad': 'Grad',
                   'inpgrad': 'InpGrad',
                   'ig': 'IG',
                   'lime': 'Lime',
                   'mp': 'MP',
                   'occlusion': 'Occlusion',
                   'sg': 'SmoothGrad',
                   }
    method_name = method_dict[args.method_name]

    metric_file_paths = [os.path.join(args.input_dir_path,
                               f'Method_{method_name}_Metric_{i}') for i in ['ssim', 'hog', 'spearman']]

    assert all([os.path.isdir(i) for i in metric_file_paths]) == True, \
        'Something is wrong with the input path'

    model_name_dir_flag = False

    empty_dict = {'pytorch': [],
                 'googlenet': [],
                 'madry': [],
                  }

    data_dicts = {'ssim': {'mean_dict': deepcopy(empty_dict), 'var_dict': deepcopy(empty_dict)},
                  'hog': {'mean_dict': deepcopy(empty_dict), 'var_dict': deepcopy(empty_dict)},
                  'spearman': {'mean_dict': deepcopy(empty_dict), 'var_dict': deepcopy(empty_dict)},
                  }

    ## List for asserting the order of read
    order_list = ['googlenet', 'madry', 'pytorch']
    for input_path in metric_file_paths:
        metric_name = input_path.split('/')[-1].split('_')[-1]
        txt_data_files = glob.glob(os.path.join(input_path,
                                                f'*_Model_*_{method_name}_{metric_name}*.txt'))
        txt_data_files.sort()

        mean_dict = deepcopy(empty_dict)
        var_dict = deepcopy(empty_dict)

        ## Data read
        print(f'Reading Data ... ', end='')
        for modelIdx, model_name in enumerate(order_list):
            txt_file = txt_data_files[modelIdx]
            assert model_name in txt_file.split('/')[-1].split('_'), 'Something wrong with the reading of data. Check'
            with open(txt_file, 'r') as f:
                data_list = f.read().splitlines()
                data_list = data_list[1:2001]

                [(mean_dict[model_name].append(float(i.split(',')[1])),
                  var_dict[model_name].append(float(i.split(',')[2])))
                 for i in data_list]
        print(f'Done')

        ## Check for NAN
        orig_len = len(mean_dict['googlenet'])
        # ipdb.set_trace()
        pNans = np.argwhere(np.isnan(mean_dict['pytorch']))
        mNans = np.argwhere(np.isnan(mean_dict['madry']))
        gNans = np.argwhere(np.isnan(mean_dict['googlenet']))

        nan_idxs = reduce(np.union1d, (pNans, mNans, gNans))

        for data in [mean_dict, var_dict]:
            for key in data.keys():
                data[key] = np.delete(data[key], nan_idxs).tolist()

        f_len = orig_len - len(nan_idxs)
        for data in [mean_dict, var_dict]:
            for key in data.keys():
                assert np.isnan(data[key]).any() == False, 'Something is worng in checking for nans'
                assert len(data[key]) == f_len, 'Something is worng in checking for nans'

        print(f'Nans removed.\nFinal no of images are {f_len}/{orig_len}')

        data_dicts[metric_name]['mean_dict'] = mean_dict
        data_dicts[metric_name]['var_dict'] = var_dict

    ## Plotting

    ## Error Bar Plot
    print(f'Plotting ErrorBar Plot ... ')
    dName = args.out_path
    fName = f'time_{f_time}_Error_Plot_Combined_Method_{method_name}.png'
    combined_errorbar_plot(data_dicts, fName=fName, out_dir=dName, save=args.save)
    print(f'Done')
    #################################################################################

    print(f'Time taken is {time.time() - s_time}')
    print(f'Time stamp is {f_time}\n')

########################################################################################################################



