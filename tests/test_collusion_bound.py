from __future__ import annotations

import math
import unittest

from src.collusion_bound import Annotation, LabelCollusionBound


class CollusionTests(unittest.TestCase):
    @staticmethod
    def identical_ring(n: int = 30):
        rows = []
        for i in range(n):
            label = "cat" if i % 2 == 0 else "dog"
            rows.append(Annotation("a1", f"i{i}", label))
            rows.append(Annotation("a2", f"i{i}", label))
            rows.append(
                Annotation("a3", f"i{i}", "cat" if i % 3 == 0 else "dog")
            )
        return rows

    def test_detects_identical_ring(self):
        report = LabelCollusionBound(margin=0.2, min_overlap=20).analyze(
            self.identical_ring()
        )
        flagged_ids = {(pair.a, pair.b) for pair in report.flagged_pairs}
        self.assertIn(("a1", "a2"), flagged_ids)

    def test_chance_uses_independent_annotator_marginals(self):
        rows = []
        for i in range(10):
            rows.append(Annotation("a", f"i{i}", "cat"))
            rows.append(Annotation("b", f"i{i}", "cat" if i < 5 else "dog"))
        report = LabelCollusionBound(margin=0.1, min_overlap=10).analyze(rows)
        pair = report.pairs[0]
        self.assertEqual(pair.agreement, 0.5)
        self.assertEqual(pair.chance, 0.5)
        self.assertEqual(pair.lift, 0.0)
        self.assertFalse(pair.flagged)

    def test_duplicate_annotator_item_refuses(self):
        with self.assertRaisesRegex(ValueError, "duplicate annotation"):
            LabelCollusionBound(min_overlap=1).analyze(
                [
                    Annotation("a", "i1", "cat"),
                    Annotation("a", "i1", "dog"),
                ]
            )

    def test_empty_dimensions_refuse(self):
        bad_rows = [
            Annotation("", "i", "cat"),
            Annotation("a", "", "cat"),
            Annotation("a", "i", ""),
        ]
        for row in bad_rows:
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    LabelCollusionBound(min_overlap=1).analyze([row])

    def test_policy_is_bound_into_report(self):
        rows = self.identical_ring()
        first = LabelCollusionBound(margin=0.2, min_overlap=20).analyze(rows)
        second = LabelCollusionBound(margin=0.3, min_overlap=20).analyze(rows)
        self.assertNotEqual(first.policy_fingerprint, second.policy_fingerprint)
        self.assertNotEqual(first.fingerprint, second.fingerprint)

    def test_input_is_bound_into_report(self):
        first = LabelCollusionBound(margin=0.2, min_overlap=2).analyze(
            [
                Annotation("a", "i1", "cat"),
                Annotation("b", "i1", "cat"),
                Annotation("a", "i2", "dog"),
                Annotation("b", "i2", "dog"),
            ]
        )
        second = LabelCollusionBound(margin=0.2, min_overlap=2).analyze(
            [
                Annotation("x", "j1", "cat"),
                Annotation("y", "j1", "cat"),
                Annotation("x", "j2", "dog"),
                Annotation("y", "j2", "dog"),
            ]
        )
        self.assertNotEqual(first.input_fingerprint, second.input_fingerprint)
        self.assertNotEqual(first.fingerprint, second.fingerprint)

    def test_invalid_policy_refuses(self):
        for margin in (-0.1, 1.1, math.inf, math.nan):
            with self.subTest(margin=margin):
                with self.assertRaises(ValueError):
                    LabelCollusionBound(margin=margin)
        with self.assertRaises(ValueError):
            LabelCollusionBound(min_overlap=0)


if __name__ == "__main__":
    unittest.main()
