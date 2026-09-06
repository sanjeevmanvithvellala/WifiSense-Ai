"""
Lightweight Transformer CSI Classifier.
Self-attention model capturing multi-subcarrier cross-attention and temporal dependencies.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.models.base import BaseCSIModel


class _PyTorchTransformer(nn.Module):
    def __init__(self, in_features: int, num_classes: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2):
        super().__init__()
        self.input_proj = nn.Linear(in_features, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=128,
            dropout=0.1,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # x shape: (Batch, seq_len, in_features)
        h = self.input_proj(x)
        encoded = self.transformer_encoder(h)  # (Batch, seq_len, d_model)
        # Global average pool across sequence
        pooled = torch.mean(encoded, dim=1)
        out = self.classifier(pooled)
        return out


class TransformerCSIClassifier(BaseCSIModel):
    """Lightweight Transformer-based CSI HAR Classifier."""

    def __init__(
        self,
        model_id: str = "transformer_01",
        name: str = "Transformer CSI Classifier",
        epochs: int = 8,
        batch_size: int = 32,
        lr: float = 0.001,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        in_features: int = 64
    ):
        super().__init__(model_id, name, "Transformer")
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.in_features = in_features
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net: Optional[_PyTorchTransformer] = None

    def _format_input(self, X: np.ndarray) -> torch.Tensor:
        if X.ndim == 3:
            # (Batch, seq_len, subcarriers)
            N, T, S = X.shape
            self.in_features = S
            x_tensor = torch.tensor(X, dtype=torch.float32)
        elif X.ndim == 2:
            # (Batch, features) -> treat as (Batch, 1, features)
            x_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
            self.in_features = X.shape[1]
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

        self.net = _PyTorchTransformer(
            in_features=self.in_features,
            num_classes=len(self.classes_),
            d_model=self.d_model,
            nhead=self.nhead,
            num_layers=self.num_layers
        ).to(self.device)

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
            "in_features": self.in_features,
            "d_model": self.d_model,
            "nhead": self.nhead,
            "num_layers": self.num_layers,
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
        self.in_features = data["in_features"]
        self.d_model = data.get("d_model", 64)
        self.nhead = data.get("nhead", 4)
        self.num_layers = data.get("num_layers", 2)
        self.is_trained = data["is_trained"]
        self.training_metadata = data.get("training_metadata", {})
        if data.get("state_dict") is not None:
            self.net = _PyTorchTransformer(
                in_features=self.in_features,
                num_classes=len(self.classes_),
                d_model=self.d_model,
                nhead=self.nhead,
                num_layers=self.num_layers
            ).to(self.device)
            self.net.load_state_dict(data["state_dict"])
            self.net.eval()
