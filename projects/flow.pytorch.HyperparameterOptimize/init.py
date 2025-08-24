import itertools
import os

import signac
import torchvision.transforms as transforms
from torchvision import datasets
from tqdm import tqdm

PR = signac.init_project()
HYPER_PARAMS = {
    "seed": [1],
    "epochs": [10, 20, 30, 40],
    "batch_size": [64],
    "lr": [0.0001, 0.0005, 0.001, 0.005, 0.01],
    "hidden_dim": [128, 256, 512],
    "latent_dim": [16],
}


def download_MNIST():
    # transforms
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
        ]
    )

    # train and validation data
    datasets.MNIST(root="./source/data", train=True, download=True, transform=transform)
    datasets.MNIST(
        root="./source/data", train=False, download=True, transform=transform
    )


def generate_workspace(pr, hyper_params):
    for sp in cartesian(**hyper_params):
        pr.open_job(sp).init()


def cartesian(**kwargs):
    for combo in tqdm(itertools.product(*kwargs.values())):
        yield dict(zip(kwargs.keys(), combo))


if __name__ == "__main__":
    generate_workspace(PR, HYPER_PARAMS)
    if not os.path.exists("./source/data/MNIST"):
        download_MNIST()
