from __future__ import annotations

import numpy as np


class MLPFromScratch:
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        self.w1 = rng.normal(0, 0.1, (input_dim, hidden_dim))
        self.b1 = np.zeros((1, hidden_dim))
        self.w2 = rng.normal(0, 0.1, (hidden_dim, output_dim))
        self.b2 = np.zeros((1, output_dim))

    def relu(self, values: np.ndarray) -> np.ndarray:
        return np.maximum(0, values)

    def softmax(self, values: np.ndarray) -> np.ndarray:
        shifted = values - np.max(values, axis=1, keepdims=True)
        exp = np.exp(shifted)
        return exp / np.sum(exp, axis=1, keepdims=True)

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        z1 = x @ self.w1 + self.b1
        a1 = self.relu(z1)
        z2 = a1 @ self.w2 + self.b2
        probs = self.softmax(z2)
        return z1, a1, probs

    def cross_entropy(self, probs: np.ndarray, y: np.ndarray) -> float:
        epsilon = 1e-9
        return float(-np.mean(np.sum(y * np.log(probs + epsilon), axis=1)))

    def backward(self, x: np.ndarray, y: np.ndarray, z1: np.ndarray, a1: np.ndarray, probs: np.ndarray) -> None:
        n = x.shape[0]
        dz2 = (probs - y) / n
        dw2 = a1.T @ dz2
        db2 = np.sum(dz2, axis=0, keepdims=True)
        da1 = dz2 @ self.w2.T
        dz1 = da1 * (z1 > 0)
        dw1 = x.T @ dz1
        db1 = np.sum(dz1, axis=0, keepdims=True)
        lr = 0.05
        self.w2 -= lr * dw2
        self.b2 -= lr * db2
        self.w1 -= lr * dw1
        self.b1 -= lr * db1

    def fit(self, x: np.ndarray, y: np.ndarray, epochs: int = 100) -> list[float]:
        losses: list[float] = []
        for _ in range(epochs):
            z1, a1, probs = self.forward(x)
            loss = self.cross_entropy(probs, y)
            losses.append(loss)
            self.backward(x, y, z1, a1, probs)
        return losses

    def predict(self, x: np.ndarray) -> np.ndarray:
        _, _, probs = self.forward(x)
        return np.argmax(probs, axis=1)


if __name__ == "__main__":
    x = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]], dtype=float)
    y = np.array([[1, 0], [0, 1], [0, 1], [1, 0]], dtype=float)
    model = MLPFromScratch(3, 5, 2)
    losses = model.fit(x, y, epochs=200)
    print(losses[0], losses[-1])
