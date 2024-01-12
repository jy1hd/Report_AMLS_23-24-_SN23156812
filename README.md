·Hello :),Thanks for using or verifying my code and model


·The main.py will be used for receiving the model parameters you selected, and start to execute the corresponding functions.
How to use main.py : 
	If you want to use CNN_MLP (Folder A),just input command "python main.py --comparison_type=CNN_MLP".
	If you want to use CNN_RF (Folder B),just input command "python main.py --comparison_type=CNN_RF"


·The packages required to run the code:

1.medmnist
2.numpy
3.PIL(Pillow)
4.torch (Pytorch)
5.torchvision
6.tensorboardX
7.tqdm
8.seaborn

·Folder A stores the model code (MLP and CNN models) of the PnemoniaMNIST data set, and Folder B stores the test model code (CNN and RF) of the PathMNIST data set.
（When running the Random Forest model of Folder B, the fit operation takes a while because the CPU is used instead of the GPU, and the data set is a bit large, so you need to wait for a while.）
