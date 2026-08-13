from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class ModelArtifact:
    name: str
    version: str
    feature_set_version: str
    dataset_version: str
    metrics: dict[str, float]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ModelArtifact] = {}

    def register(self, artifact: ModelArtifact) -> str:
        key = f"{artifact.name}:{artifact.version}"
        self._items[key] = artifact
        return key

    def get(self, key: str) -> ModelArtifact | None:
        return self._items.get(key)


class RolloutController:
    def __init__(self) -> None:
        self.stage = "shadow"

    def next_stage(self, *, shadow_ok: bool, canary_ok: bool) -> str:
        if self.stage == "shadow" and shadow_ok:
            self.stage = "canary"
        elif self.stage == "canary" and canary_ok:
            self.stage = "production"
        return self.stage
