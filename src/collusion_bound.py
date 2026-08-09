
"""Label collusion bound — flag super-chance annotator agreement."""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Annotation:
    annotator_id: str
    item_id: str
    label: str


@dataclass(frozen=True)
class PairReport:
    a: str
    b: str
    n_overlap: int
    agreement: float
    chance: float
    lift: float
    flagged: bool


@dataclass(frozen=True)
class CollusionReport:
    pairs: tuple[PairReport, ...]
    flagged_pairs: tuple[PairReport, ...]
    fingerprint: str


class LabelCollusionBound:
    """Flag annotator pairs whose agreement exceeds chance + margin."""

    def __init__(self, margin: float = 0.25, min_overlap: int = 20):
        if not 0 < margin < 1:
            raise ValueError("margin must be in (0,1)")
        self.margin = margin
        self.min_overlap = min_overlap

    def _chance(self, labels_a: Sequence[str], labels_b: Sequence[str]) -> float:
        # expected agreement under independent draws from pooled empirical prior on overlap items
        all_labels = list(labels_a) + list(labels_b)
        n = len(all_labels)
        if n == 0:
            return 0.0
        freq = Counter(all_labels)
        return sum((c / n) ** 2 for c in freq.values())

    def analyze(self, rows: Iterable[Annotation]) -> CollusionReport:
        by_ann: dict[str, dict[str, str]] = {}
        for r in rows:
            by_ann.setdefault(r.annotator_id, {})[r.item_id] = r.label
        ids = sorted(by_ann)
        pairs: list[PairReport] = []
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                common = sorted(set(by_ann[a]) & set(by_ann[b]))
                if len(common) < self.min_overlap:
                    continue
                la = [by_ann[a][k] for k in common]
                lb = [by_ann[b][k] for k in common]
                agree = sum(x == y for x, y in zip(la, lb)) / len(common)
                chance = self._chance(la, lb)
                lift = agree - chance
                flagged = lift >= self.margin
                pairs.append(
                    PairReport(a, b, len(common), agree, chance, lift, flagged)
                )
        flagged = tuple(p for p in pairs if p.flagged)
        fp = digest(
            {
                "pairs": [(p.a, p.b, round(p.agreement, 6), p.flagged) for p in pairs],
                "margin": self.margin,
            }
        )
        return CollusionReport(tuple(pairs), flagged, fp)
