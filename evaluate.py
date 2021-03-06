import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from data_utils import json_in_train, json_in_test


def check_train(train_dir):
    train_data, height, width, max_ = json_in_train(train_dir)

    plt.hist(train_data.flatten())
    plt.savefig('./train_distribution.png')

    return None


def check_pred(pred_dir, back_dir, type, images_dir):
    test_data, H, W = json_in_test(back_dir, type)
    print('test shape', test_data.shape)
    print('test non-zero: \n', test_data[test_data > 0].shape[0])

    pred_data, H, W = json_in_test(pred_dir, type)
    print('pred shape', pred_data.shape)
    print('pred non-zero: \n', pred_data[np.nonzero(pred_data)].shape[0])

    # print images
    step = 1
    # ground truth
    for i in range(timesteps + step):
        plt.imshow(test_data[step+i,:,:,0])
        plt.savefig(os.path.join(images_dir, str(i)+'.png'))

    # predicted value
    plt.imshow(pred_data[step,:,:,0])
    plt.savefig(os.path.join(images_dir, str(i)+'_pred.png'))

    return None


def evaluate_result(pred_dir, test_dir, type):
    pred_data, H_pred, W_pred = json_in_test(pred_dir, type)
    test_data, H_test, W_test = json_in_test(test_dir, type)
    assert H_pred == H_test, 'pred-test not in same dimension: H'
    assert W_pred == W_test, 'pred-test not in same dimension: W'

    # seq for evaluation
    y_pred = pred_data[:-1]
    y_true = test_data[1:]
    assert y_pred.shape == y_true.shape, 'pred-true not in same dimension'+str(y_pred.shape)+str(y_true.shape)

    mse_lst = []
    # evaluate on every timestamp
    for t in range(y_pred.shape[0]):
        print('Evaluating timestamp ', t)
        y_pred_t, y_true_t = y_pred[t,:,:,:], y_true[t,:,:,:]

        y_pred_t_mask = y_pred_t[(y_true_t > 0).all(axis=-1)]    # y_pred masked by (y_true > 0)
        y_true_t_nonz = y_true_t[y_true_t > 0]
        mse_t = ((y_pred_t_mask - y_true_t_nonz)**2).mean(axis=None)
        print('MSE: ', round(mse_t, 4))
        mse_lst.append(mse_t)

    # plot MSE
    x = range(y_pred.shape[0])
    y = mse_lst
    plt.plot(x, y)
    plt.title('MSE along Time')
    #plt.show()
    plt.savefig(pred_dir+'/eval_MSE_plot.png')

    #mse = ((y_pred - y_true)**2).mean(axis=None)
    #print('Sequence MSE:', round(mse, 4))

    return None


# global
timesteps = 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-type', '--which_type', default = 'normalize', type = str,
                        choices = ['count', 'stay', 'normalize'], help = "'count' or 'stay' or 'normalize'")
    parser.add_argument('-id', '--user_ID', type = str, help = 'Specify user ID')
    parser.add_argument('-name', '--user_name', type = str, help = 'Specify user name')

    args = parser.parse_args()

    # model name depends on which_type
    if args.which_type in ['count']:
        modelName = 'STResNet'
    elif args.which_type in ['stay', 'normalize']:
        modelName = 'ConvLSTM'

    trainPath = './' + args.user_ID + '/jsonfile'
    outputPath = './' + args.user_ID + '/backup'
    backPath = './' + args.user_ID + '/oldbackup'
    imgPath = './' + args.user_ID + '/images/' + modelName

    #check_train(trainPath)
    #check_pred(outputPath, backPath, args.which_type, imgPath)
    evaluate_result(outputPath, backPath, args.which_type)


if __name__ == '__main__':
    main()
