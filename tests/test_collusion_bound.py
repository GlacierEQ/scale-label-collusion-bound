
from __future__ import annotations
import unittest
from src.collusion_bound import Annotation, LabelCollusionBound

class CollusionTests(unittest.TestCase):
    def test_detects_identical_ring(self):
        rows = []
        for i in range(30):
            lab = "cat" if i % 2 == 0 else "dog"
            rows.append(Annotation("a1", f"i{i}", lab))
            rows.append(Annotation("a2", f"i{i}", lab))  # perfect copy
            rows.append(Annotation("a3", f"i{i}", "cat" if i % 3 == 0 else "dog"))
        rep = LabelCollusionBound(margin=0.2, min_overlap=20).analyze(rows)
        flagged_ids = {(p.a, p.b) for p in rep.flagged_pairs}
        self.assertIn(("a1", "a2"), flagged_ids)

if __name__ == "__main__":
    unittest.main()
