"""
Deep Autoencoder Anomaly Detector for Wi-Fi CSI Signals.
Reconstructs normal CSI patterns; high reconstruction error signals anomalous activity or signal corruption.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, Any, Optional
from ml.models.base import BaseAnomalyDetector


class _PyTorchAutoencoder(nn.Module):
    def __init__(self, in_features: int, latent_dim: int = 16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, in_features)
        )

    def forward(self, x):
        z = self.encoder(x)
        recon = self.decoder(z)
        return recon


class AutoencoderAnomalyDetector(BaseAnomalyDetector):
    """Deep Autoencoder reconstruction-based anomaly detector."""

    def __init__(
        self,
        model_id: str = "autoencoder_01",
        name: str = "Deep Autoencoder Anomaly Detector",
        epochs: int = 20,
        batch_size: int = 32,
        lr: float = 0.001,
        latent_dim: int = 16,
        in_features: int = 64
    ):
        super().__init__(model_id, name, "Deep Autoencoder")
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.latent_dim = latent_dim
        self.in_features = in_features
        self.threshold = 0.5
        self.recon_scale = 1.0
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net: Optional[_PyTorchAutoencoder] = None

    def _format_input(self, X: np.ndarray) -> torch.Tensor:
        if X.ndim == 3:
            # Flatten window (N, T, S) -> (N, T*S)
            N = X.shape[0]
            flat_X = X.reshape(N, -1)
            self.in_features = flat_X.shape[1]
            return torch.tensor(flat_X, dtype=torch.float32)
        elif X.ndim == 2:
            self.in_features = X.shape[1]
            return torch.tensor(X, dtype=torch.float32)
        else:
            raise ValueError(f"Invalid dimension {X.ndim}")

    def fit(self, X: np.ndarray, **kwargs) -> Dict[str, Any]:
        X_t = self._format_input(X)
        dataset = TensorDataset(X_t)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.net = _PyTorchAutoencoder(self.in_features, self.latent_dim).to(self.device)
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=1e-5)

        self.net.train()
        for epoch in range(self.epochs):
            for (batch_x,) in dataloader:
                batch_x = batch_x.to(self.device)
                optimizer.zero_grad()
                recon = self.net(batch_x)
                loss = criterion(recon, batch_x)
                loss.backward()
                optimizer.step()

        self.is_trained = True

        # Calibrate baseline MSE scale
        self.net.eval()
        with torch.no_grad():
            full_recon = self.net(X_t.to(self.device))
            mse_vals = torch.mean((full_recon - X_t.to(self.device)) ** 2, dim=-1).cpu().numpy()
            self.recon_scale = float(np.percentile(mse_vals, 95)) + 1e-6

        return {
            "model_id": self.model_id,
            "algorithm": self.algorithm,
            "latent_dim": self.latent_dim,
            "in_features": self.in_features,
            "epochs": self.epochs,
            "baseline_recon_scale": self.recon_scale
        }

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained or self.net is None:
            return np.zeros(len(X), dtype=np.float32)

        self.net.eval()
        X_t = self._format_input(X).to(self.device)
        with torch.no_grad():
            recon = self.net(X_t)
            mse_vals = torch.mean((recon - X_t) ** 2, dim=-1).cpu().numpy()

        # Normalize score to [0, 1] relative to normal baseline reconstruction
        norm_scores = 1.0 - np.exp(-mse_vals / (self.recon_scale + 1e-6))
        return np.clip(norm_scores, 0.0, 1.0).astype(np.float32)

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            "model_id": self.model_id,
            "name": self.name,
            "algorithm": self.algorithm,
            "latent_dim": self.latent_dim,
            "in_features": self.in_features,
            "threshold": self.threshold,
            "recon_scale": self.recon_scale,
            "is_trained": self.is_trained,
            "state_dict": self.net.state_dict() if self.net else None
        }, filepath)

    def load(self, filepath: str):
        data = torch.load(filepath, map_location=self.device)
        self.model_id = data["model_id"]
        self.name = data["name"]
        self.algorithm = data["algorithm"]
        self.latent_dim = data["latent_dim"]
        self.in_features = data["in_features"]
        self.threshold = data.get("threshold", 0.5)
        self.recon_scale = data.get("recon_scale", 1.0)
        self.is_trained = data["is_trained"]
        if data.get("state_dict") is not None:
            self.net = _PyTorchAutoencoder(self.in_features, self.latent_dim).to(self.device)
            self.net.load_state_dict(data["state_dict"])
            self.net.eval()
