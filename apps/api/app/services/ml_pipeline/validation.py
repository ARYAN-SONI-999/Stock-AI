from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WalkForwardSplit:
    train_start: int
    train_end: int
    val_start: int
    val_end: int
    test_start: int
    test_end: int


def build_walk_forward_splits(
    total_rows: int,
    *,
    train_size: int,
    val_size: int,
    test_size: int,
    step_size: int,
) -> list[WalkForwardSplit]:
    if min(total_rows, train_size, val_size, test_size, step_size) <= 0:
        return []

    splits: list[WalkForwardSplit] = []
    train_start = 0

    while True:
        train_end = train_start + train_size
        val_start = train_end
        val_end = val_start + val_size
        test_start = val_end
        test_end = test_start + test_size

        if test_end > total_rows:
            break

        splits.append(
            WalkForwardSplit(
                train_start=train_start,
                train_end=train_end,
                val_start=val_start,
                val_end=val_end,
                test_start=test_start,
                test_end=test_end,
            )
        )
        train_start += step_size

    return splits
