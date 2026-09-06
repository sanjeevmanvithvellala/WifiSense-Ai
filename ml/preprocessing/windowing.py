"""
Temporal sliding window segmentation for CSI time series.
"""

import numpy as np
from typing import List, Tuple, Optional


def create_sliding_windows(
    data: np.ndarray,
    window_size: int = 50,
    overlap_ratio: float = 0.5,
    stride: Optional[int] = None
) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Segments a 2D CSI array (time_steps, subcarriers) into 3D array of windows: (num_windows, window_size, subcarriers).
    
    Args:
        data: 2D array of shape (T, S)
        window_size: Number of time samples per window (e.g. 50 samples at 50Hz = 1.0s)
        overlap_ratio: Overlap fraction (0.0 to 0.9)
        stride: Explicit step size between window starts. If provided, overrides overlap_ratio.
        
    Returns:
        windows: 3D array (num_windows, window_size, subcarriers)
        indices: List of (start_idx, end_idx) tuples for each window
    """
    total_steps = data.shape[0]
    if total_steps < window_size:
        # If shorter than one window, pad with edge values or return single padded window
        pad_width = ((0, window_size - total_steps), (0, 0)) if data.ndim == 2 else ((0, window_size - total_steps),)
        padded = np.pad(data, pad_width, mode="edge")
        return np.expand_dims(padded, axis=0), [(0, total_steps)]

    if stride is None:
        stride = max(1, int(window_size * (1.0 - overlap_ratio)))

    windows_list = []
    indices_list = []
    
    start = 0
    while start + window_size <= total_steps:
        end = start + window_size
        windows_list.append(data[start:end])
        indices_list.append((start, end))
        start += stride

    # If remainder at the end is not empty and no windows were created, add last window
    if len(windows_list) == 0:
        windows_list.append(data[-window_size:])
        indices_list.append((total_steps - window_size, total_steps))

    windows = np.array(windows_list, dtype=np.float32)
    return windows, indices_list
