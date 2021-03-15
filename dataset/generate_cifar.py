import numpy as np
import os
import sys
import random
import torch
import torchvision
import torchvision.transforms as transforms
from utils.dataset_utils import check, seperete_data, split_data, save_file


random.seed(1)
np.random.seed(1)
num_clients = 50
num_labels = 10
dir_path = "Cifar10/"


# Allocate data to users
def generate_cifar(dir_path=dir_path, num_clients=num_clients, num_labels=num_labels, niid=False, real=True):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        
    # Setup directory for train/test data
    config_path = dir_path + "config.json"
    train_path = dir_path + "train/train.json"
    test_path = dir_path + "test/test.json"

    if check(config_path, train_path, test_path, num_clients, num_labels, niid, real):
        return
        
    # Get Cifar10 data
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    trainset = torchvision.datasets.CIFAR10(
        root=dir_path+"rawdata", train=True, download=True, transform=transform)
    testset = torchvision.datasets.CIFAR10(
        root=dir_path+"rawdata", train=False, download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(
        trainset, batch_size=len(trainset.data), shuffle=False)
    testloader = torch.utils.data.DataLoader(
        testset, batch_size=len(testset.data), shuffle=False)

    for _, train_data in enumerate(trainloader, 0):
        trainset.data, trainset.targets = train_data
    for _, test_data in enumerate(testloader, 0):
        testset.data, testset.targets = test_data

    dataset_image = []
    dataset_label = []

    dataset_image.extend(trainset.data.cpu().detach().numpy())
    dataset_image.extend(testset.data.cpu().detach().numpy())
    dataset_label.extend(trainset.targets.cpu().detach().numpy())
    dataset_label.extend(testset.targets.cpu().detach().numpy())
    dataset_image = np.array(dataset_image)
    dataset_label = np.array(dataset_label)

    dataset = []
    for i in range(10):
        idx = dataset_label == i
        dataset.append(dataset_image[idx])

    
    X, y, statistic = seperete_data(dataset, num_clients, num_labels, niid, real)
    train_data, test_data = split_data(X, y, num_clients)
    save_file(config_path, train_path, test_path, train_data, test_data, num_clients, num_labels, statistic, niid, real)


if __name__ == "__main__":
    niid = True if sys.argv[1] == "noniid" else False
    real = True if sys.argv[2] == "realworld" else False

    generate_cifar(dir_path=dir_path, num_clients=num_clients, num_labels=num_labels, niid=niid, real=real)