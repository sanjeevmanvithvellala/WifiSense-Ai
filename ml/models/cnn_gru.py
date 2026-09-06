"""
CNN + GRU Hybrid Model for Wi-Fi CSI Activity Recognition.
Leverages Conv1D feature extractors with recurrent GRU temporal memory.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.models.base import BaseCSIModel


class _PyTorchCNNGRU(nn.Module):
    def __init__(self, in_channels: int, num_classes: int, hidden_dim: int = 64, num_layers: int = 1):
        super().__init__()
        # Conv block reduces temporal resolution and extracts spatial features
        self.conv = nn.Sequential(
            nn.Conv1d(in_channels, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        self.gru = nn.GRU(
            input_size=64,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        self.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(hidden_dim * 2, num_classes)
        )

    def forward(self, x):
        # x shape: (Batch, in_channels, seq_len)
        feats = self.conv(x)  # (Batch, 64, seq_len // 2)
        feats_seq = feats.permute(0, 2, 1)  # (Batch, seq_len // 2, 64)
        gru_out, _ = self.gru(feats_seq)  # (Batch, seq_len // 2, hidden_dim * 2)
        # Take last time step
        last_step = gru_out[:, -1, :]
        out = self.fc(last_step)
        return out


class CNNGRUClassifier(BaseCSIModel):
    """Hybrid CNN + Bidirectional GRU model."""

    def __init__(
        self,
        model_id: str = "cnn_gru_01",
        name: str = "CNN-GRU CSI Classifier",
        epochs: int = 8,
        batch_size: int = 32,
        lr: float = 0.001,
        hidden_dim: int = 64,
        in_channels: int = 64
    ):
        super().__init__(model_id, name, "CNN-GRU")
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.hidden_dim = hidden_dim
        self.in_channels = in_channels
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net: Optional[_PyTorchCNNGRU] = None

    def _format_input(self, X: np.ndarray) -> torch.Tensor:
        if X.ndim == 3:
            N, T, S = X.shape
            self.in_channels = S
            x_tensor = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)
        elif X.ndim == 2:
            x_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
            self.in_channels = 1
        else:
            raise ValueError(f"Unsupported input dimension {X.ndim}")
        return x_tensor

    def train(
        self,
        X: np.ndarray,
        y: List[str] | np.ndarray,
        validation_data: Optional[Tuple[np.ndarray, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        y_arr = np.array(y)
        self.classes_ = sorted(list(set(y_arr)))
        label_to_idx = {lbl: i for i, lbl in enumerate(self.classes_)}
        y_indices = np.array([label_to_idx[lbl] for lbl in y_arr])

        X_t = self._format_input(X)
        y_t = torch.tensor(y_indices, dtype=torch.long)

        dataset = TensorDataset(X_t, y_t)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.net = _PyTorchCNNGRU(self.in_channels, len(self.classes_), self.hidden_dim).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=1e-4)

        self.net.train()
        for epoch in range(self.epochs):
            for batch_x, batch_y in dataloader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                optimizer.zero_grad()
                outputs = self.net(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

        self.is_trained = True
        train_metrics = self.evaluate(X, y_arr)
        val_metrics = self.evaluate(validation_data[0], validation_data[1]) if validation_data is not None else None

        self.training_metadata = {
            "model_id": self.model_id,
            "architecture": self.architecture,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "train_metrics": train_metrics,
            "val_metrics": val_metrics,
            "classes": self.classes_,
        }
        return self.training_metadata

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained or self.net is None:
            raise RuntimeError("Model is not trained.")
        self.net.eval()
        X_t = self._format_input(X).to(self.device)
        with torch.no_grad():
            logits = self.net(X_t)
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
        return probs

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        pred_idx = np.argmax(probs, axis=-1)
        return np.array([self.classes_[idx] for idx in pred_idx])

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            "model_id": self.model_id,
            "name": self.name,
            "architecture": self.architecture,
            "classes": self.classes_,
            "in_channels": self.in_channels,
            "hidden_dim": self.hidden_dim,
            "is_trained": self.is_trained,
            "training_metadata": self.training_metadata,
            "state_dict": self.net.state_dict() if self.net else None
        }, filepath)

    def load(self, filepath: str):
        data = torch.load(filepath, map_location=self.device)
        self.model_id = data["model_id"]
        self.name = data["name"]
        self.architecture = data["architecture"]
        self.classes_ = data["classes"]
        self.in_channels = data["in_channels"]
        self.hidden_dim = data.get("hidden_dim", 64)
        self.is_trained = data["is_trained"]
        self.training_metadata = data.get("training_metadata", {})
        if data.get("state_dict") is not None:
            self.net = _PyTorchCNNGRU(self.in_channels, len(self.classes_), self.hidden_dim).to(self.device)
            self.net.load_state_dict(data["state_dict"])
            self.net.eval()
