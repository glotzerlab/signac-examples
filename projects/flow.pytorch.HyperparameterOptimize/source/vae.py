import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision import datasets


class LinearVAE(nn.Module):
    def __init__(self, features_dim, latent_dim, hidden_dim):
        super().__init__()

        self.latent_dim = latent_dim
        # encoder
        self.enc1 = nn.Linear(in_features=features_dim, out_features=hidden_dim)
        self.enc2 = nn.Linear(in_features=hidden_dim, out_features=latent_dim * 2)

        # decoder
        self.dec1 = nn.Linear(in_features=latent_dim, out_features=hidden_dim)
        self.dec2 = nn.Linear(in_features=hidden_dim, out_features=features_dim)

    def reparameterize(self, mu, log_var):
        """
        :param mu: mean from the encoder's latent space
        :param log_var: log variance from the encoder's latent space
        """
        std = torch.exp(0.5 * log_var)  # standard deviation
        eps = torch.randn_like(std)  # "randn_like" as we need the same size
        sample = mu + (eps * std)  # sampling as if coming from the input space

        return sample

    def sample(self, x):
        with torch.no_grad():
            return self.reparameterize(*self.encode(x))

    def forward(self, x):
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        reconstruction = self.decode(z)

        return reconstruction, mu, log_var

    def encode(self, x):
        x = F.relu(self.enc1(x))
        x = self.enc2(x).view(-1, self.latent_dim, 2)

        mu = x[:, :, 0]  # the first feature values as mean
        log_var = x[:, :, 1]  # the other feature values as variance
        return mu, log_var

    def decode(self, z):
        x = F.relu(self.dec1(z))
        reconstruction = torch.sigmoid(self.dec2(x))
        return reconstruction

    @classmethod
    def from_job(cls, job, device, state_file="model.pth"):
        model = cls(
            job.doc["features_dim"], job.sp["latent_dim"], job.sp["hidden_dim"]
        ).to(device)
        if job.isfile("model.pth"):
            model.load_state_dict(
                torch.load(job.fn("model.pth"), map_location=device))
        return model


class VAELoss:
    def __init__(self):
        self.bce = nn.BCELoss()

    def __call__(self, input, reconstruction, mu, logvar):
        kl_divergence = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        return self.bce(reconstruction, input) + kl_divergence


def load_data(job):
    torch.manual_seed(job.sp["seed"])
    batch_size = job.sp.get("batch_size", 64)

    transform = transforms.Compose(
        [
            transforms.ToTensor(),
        ]
    )
    train_data = datasets.MNIST(
        root=job.fn("../../source/data"),
        train=True,
        download=False,
        transform=transform,
    )
    val_data = datasets.MNIST(
        root=job.fn("../../source/data"),
        train=False,
        download=False,
        transform=transform,
    )
    job.doc.setdefault(
        "features_dim", train_data[0][0].shape[1] * train_data[0][0].shape[2])

    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader


def fit(job, train_loader, val_loader, device):
    import time

    torch.manual_seed(job.sp["seed"])
    print(f"Job id: {job.id}")
    start_time = time.time()
    epochs = job.sp.get("epochs", 1)

    model = LinearVAE.from_job(job, device)
    optimizer = optim.Adam(model.parameters(), lr=job.sp.get("lr", 0.000001))
    loss_compute = VAELoss()

    train_loss = []
    val_loss = []
    for epoch in range(epochs):
        print("--------------------------------\n")
        print(f"Current epoch: {epoch+1}/{epochs}\n")
        train_epoch_loss = training(
            job, train_loader, model, device, optimizer, loss_compute
        )
        val_epoch_loss = validate(val_loader, model, device, loss_compute)
        train_loss.append(train_epoch_loss)
        val_loss.append(val_epoch_loss)

    with job.data:
        job.data["training/loss"] = np.hstack(train_loss)
        job.data["validation/loss"] = np.hstack(val_loss)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    end_time = time.time()
    job.doc["elapsed_time"] = end_time - start_time


def get_feature(data, device):
    feature, label = data
    return feature.to(device).view(feature.size(0), -1)


def step(data, device, model, loss_compute):
    feature = get_feature(data, device)
    reconstruction, mu, logvar = model(feature)
    return loss_compute(feature, reconstruction, mu, logvar)


def training(job, dataloader, model, device, optimizer, loss_compute):
    model.train()
    running_loss = 0.0
    for i, data in enumerate(dataloader):
        optimizer.zero_grad()
        loss = step(data, device, model, loss_compute)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

        torch.save(model.state_dict(), job.fn("model.pth"))
        torch.save(optimizer.state_dict(), job.fn("optimizer.ptpyth"))

    train_loss = running_loss / len(dataloader.dataset)
    print(f"Training set: Avg. loss {train_loss:.4f}\n")
    return train_loss


def validate(dataloader, model, device, loss_compute):
    model.eval()
    running_loss = 0.0
    with torch.no_grad():
        for i, data in enumerate(dataloader):
            running_loss += step(data, device, model, loss_compute).item()

    val_loss = running_loss / len(dataloader.dataset)
    print(f"Validation set: Avg. loss {val_loss:.4f}\n")
    return val_loss


def plot_loss(job):

    with job.data:
        training_loss = job.data["training/loss"][:]
        val_loss = job.data["validation/loss"][:]

    epochs = np.arange(1, job.sp["epochs"] + 1)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(epochs, training_loss, label="Training")
    ax.plot(epochs, val_loss, linestyle="--", label="Validation")
    ax.legend(fontsize=20)
    ax.set_xlabel("Epochs")
    ax.set_ylabel("KL-divergence + Reconstruction loss", fontsize=20)
    ax.set_title("Loss")
    fig.savefig(job.fn("Loss.jpg"))


def plot_latent(job, dataset, device):
    torch.manual_seed(job.sp["seed"])
    model = LinearVAE.from_job(job, device)

    x_arr = []
    label_arr = []
    for x, label in dataset:
        x_arr.append(x)
        label_arr.append(label)

    z_arr = np.vstack(
        [model.sample(xi.to(device)[0].view(1, -1)).detach().cpu().numpy()[0]
         for xi in x_arr]
    )

    colormap = mpl.cm.get_cmap("tab10")
    sm = plt.cm.ScalarMappable(cmap=colormap)
    sm.set_array([])

    # use 10 colors to represent a given digit
    colors = np.linspace(0, 1, 10, endpoint=False)
    c_arr = colormap(colors[np.asarray(label_arr)])

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.scatter(z_arr[:, 0], z_arr[:, 1], c=c_arr, s=5)
    plt.colorbar(sm, ax=ax, ticks=np.arange(10), label="Ground truth")
    ax.set_xlabel(r"$z_1$")
    ax.set_ylabel(r"$z_2$")
    ax.set_title("Latent space of val set")
    fig.savefig(job.fn("latent.jpg"))


def plot_reconstruction(job, dataset, plot_arrangement, device):
    torch.manual_seed(job.sp["seed"])
    model = LinearVAE.from_job(job, device)

    fig_orig, ax_orig = plt.subplots(*plot_arrangement, figsize=(14, 10))
    fig_orig.suptitle("Ground Truth")
    fig_recon, ax_recon = plt.subplots(*plot_arrangement, figsize=(14, 10))
    fig_recon.suptitle("VAE Reconstruction")


    def plot_image(torch_arr, ax):
        ax.imshow(
            torch_arr.reshape(28, 28).to("cpu").detach().numpy(),
            alpha=0.8, cmap="grey")

    rng = np.random.default_rng(job.sp["seed"])
    samples = rng.integers(0, len(dataset) - 1, np.product(plot_arrangement))
    for i, ax1, ax2 in zip(samples, ax_orig.flat, ax_recon.flat):
        feature, _ = dataset[i]
        plot_image(feature, ax1)
        with torch.no_grad():
            feature = feature.to(device).view(feature.size(0), -1)
            reconstruction, _, _ = model(feature)
            plot_image(reconstruction, ax2)
    fig_orig.savefig(job.fn("digits_orig.jpg"))
    fig_recon.savefig(job.fn("digits_recon.jpg"))
