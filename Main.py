import argparse
import os
def cnn_mlp_processing():
    print("MLP training and graphic rendering processing is started !!!")
    os.system("python ./A/PneumoniaMNIST.py")
def cnn_rf_processing():
    print("RF training and graphic rendering processing is started !!!")
    os.system("python ./B/PathMNIST.py")
def processing(local_comparison_type):
    print("Dear user, you want to use " +local_comparison_type)
    if local_comparison_type == 'CNN_MLP':
        cnn_mlp_processing()
    elif local_comparison_type == 'CNN_RF':
        cnn_rf_processing()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Machine Learning Coursework from Jiayuan Tian')

    parser.add_argument('--comparison_type',
                        default='CNN_MLP',
                        type=str)
    args = parser.parse_args()
    comparison_type = args.comparison_type
    processing(comparison_type)
