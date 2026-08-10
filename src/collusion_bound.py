"""Label-collusion bound — surface statistically unusual pairwise agreement.

This is a screening mechanism, not a misconduct adjudicator. It compares
observed pairwise agreement with the expected agreement under independent draws
from each annotator's own empirical marginal label distribution.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence


def digest(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


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
    fingerprint: str


@dataclass(frozen=True)
class CollusionReport:
    pairs: tuple[PairReport, ...]
    flagged_pairs: tuple[PairReport, ...]
    input_fingerprint: str
    policy_fingerprint: str
    fingerprint: str


class LabelCollusionBound:
    """Flag annotator pairs whose agreement lift exceeds an explicit margin."""

    def __init__(self, margin: float = 0.25, min_overlap: int = 20):
        if not math.isfinite(margin) or not 0.0 <= margin <= 1.0:
            raise ValueError("margin must be finite and in [0,1]")
        if min_overlap < 1:
            raise ValueError("min_overlap must be positive")
        self.margin = margin
        self.min_overlap = min_overlap

    @staticmethod
    def _chance(labels_a: Sequence[str], labels_b: Sequence[str]) -> float:
        """Expected agreement under independent annotator-specific marginals."""
        if len(labels_a) != len(labels_b):
            raise ValueError("pair label sequences must have equal length")
        n = len(labels_a)
        if n == 0:
            return 0.0
        freq_a = Counter(labels_a)
        freq_b = Counter(labels_b)
        labels = set(freq_a) | set(freq_b)
        return sum((freq_a[label] / n) * (freq_b[label] / n) for label in labels)

    @staticmethod
    def _normalize(rows: Iterable[Annotation]) -> tuple[Annotation, ...]:
        normalized: list[Annotation] = []
        seen: set[tuple[str, str]] = set()
        for row in rows:
            if not row.annotator_id.strip():
                raise ValueError("annotator_id must be non-empty")
            if not row.item_id.strip():
                raise ValueError("item_id must be non-empty")
            if not row.label.strip():
                raise ValueError("label must be non-empty")
            key = (row.annotator_id, row.item_id)
            if key in seen:
                raise ValueError(
                    f"duplicate annotation for annotator/item: {row.annotator_id}/{row.item_id}"
                )
            seen.add(key)
            normalized.append(row)
        return tuple(
            sorted(
                normalized,
                key=lambda row: (row.annotator_id, row.item_id, row.label),
            )
        )

    def analyze(self, rows: Iterable[Annotation]) -> CollusionReport:
        normalized = self._normalize(rows)
        by_annotator: dict[str, dict[str, str]] = {}
        for row in normalized:
            by_annotator.setdefault(row.annotator_id, {})[row.item_id] = row.label

        input_fingerprint = digest(
            [(row.annotator_id, row.item_id, row.label) for row in normalized]
        )
        policy_fingerprint = digest(
            {"margin": self.margin, "min_overlap": self.min_overlap}
        )

        annotator_ids = sorted(by_annotator)
        pairs: list[PairReport] = []
        for index, annotator_a in enumerate(annotator_ids):
            for annotator_b in annotator_ids[index + 1 :]:
                common = sorted(
                    set(by_annotator[annotator_a]) & set(by_annotator[annotator_b])
                )
                if len(common) < self.min_overlap:
                    continue
                labels_a = [by_annotator[annotator_a][item_id] for item_id in common]
                labels_b = [by_annotator[annotator_b][item_id] for item_id in common]
                agreement = sum(
                    left == right for left, right in zip(labels_a, labels_b)
                ) / len(common)
                chance = self._chance(labels_a, labels_b)
                lift = agreement - chance
                flagged = lift >= self.margin
                pair_body = {
                    "a": annotator_a,
                    "b": annotator_b,
                    "n_overlap": len(common),
                    "agreement": agreement,
                    "chance": chance,
                    "lift": lift,
                    "flagged": flagged,
                    "input_fingerprint": input_fingerprint,
                    "policy_fingerprint": policy_fingerprint,
                }
                pairs.append(
                    PairReport(
                        annotator_a,
                        annotator_b,
                        len(common),
                        agreement,
                        chance,
                        lift,
                        flagged,
                        digest(pair_body),
                    )
                )

        flagged_pairs = tuple(pair for pair in pairs if pair.flagged)
        report_body = {
            "input_fingerprint": input_fingerprint,
            "policy_fingerprint": policy_fingerprint,
            "pairs": [pair.fingerprint for pair in pairs],
        }
        return CollusionReport(
            tuple(pairs),
            flagged_pairs,
            input_fingerprint,
            policy_fingerprint,
            digest(report_body),
        )
