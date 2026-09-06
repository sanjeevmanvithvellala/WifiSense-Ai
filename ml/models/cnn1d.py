"""
1D Convolutional Neural Network for Wi-Fi CSI Temporal Windows.
PyTorch-based architecture capturing local subcarrier and temporal correlation patterns.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.models.base import BaseCSIModel


class _PyTorchCNN1D(nn.Module):
    def __init__(self, in_channels: int, num_classes: int, seq_len: int = 50):
        super().__init__()
        self.conv_block1 = nn.Sequential(
            nn.Conv1d(in_channels, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        self.conv_block2 = nn.Sequential(
            nn.Conv1d(64, 128, kernel_size=5, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        self.conv_block3 = nn.Sequential(
            nn.Conv1d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        self.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # x shape: (Batch, in_channels, seq_len)
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = x.squeeze(-1)
        out = self.fc(x)
        return out


class CNN1DCSIClassifier(BaseCSIModel):
    """1D CNN classifier operating on CSI window sequences."""

    def __init__(
        self,
        model_id: str = "cnn1d_01",
        name: str = "1D-CNN CSI Classifier",
        epochs: int = 8,
        batch_size: int = 32,
        lr: float = 0.001,
        in_channels: int = 64,
        seq_len: int = 50
    ):
        super().__init__(model_id, name, "1D CNN")
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.in_channels = in_channels
        self.seq_len = seq_len
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net: Optional[_PyTorchCNN1D] = None

    def _format_input(self, X: np.ndarray) -> torch.Tensor:
        """Converts (N, T, S) or (N, F) to (N, in_channels, seq_len)."""
        if X.ndim == 3:
            # (N, T, S) -> transpose to (N, S, T)
            N, T, S = X.shape
            self.in_channels = S
            self.seq_len = T
            x_tensor = torch.tensor(X, dtype=torch.float32).permute(0, 2, 1)
        elif X.ndim == 2:
            # Flat feature vector (N, F) -> treat as (N, 1, F)
            x_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
            self.in_channels = 1
            self.seq_len = X.shape[1]
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

        self.net = _PyTorchCNN1D(self.in_channels, len(self.classes_), self.seq_len).to(self.device)
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
            "seq_len": self.seq_len,
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
        self.seq_len = data["seq_len"]
        self.is_trained = data["is_trained"]
        self.training_metadata = data.get("training_metadata", {})
        if data.get("state_dict") is not None:
            self.net = _PyTorchCNN1D(self.in_channels, len(self.classes_), self.seq_len).to(self.device)
            self.net.load_state_dict(data["state_dict"])
            self.net.eval()
