from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text())


CANONICAL = load("machine/canonical-position.json")
CAPABILITIES = load("machine/capabilities.json")
TARGET = load("machine/target-contract.json")


class CanonicalPositionContractTests(unittest.TestCase):
    def test_repository_owns_screening_not_misconduct_adjudication(self):
        self.assertEqual(CANONICAL["role"], "CANONICAL_SPECIALIST")
        self.assertEqual(CANONICAL["owns"], "pairwise_annotator_agreement_anomaly_screening")
        self.assertIn("proof or adjudication of collusion/misconduct", CANONICAL["does_not_own"])
        self.assertIn("train/eval contamination detection", CANONICAL["does_not_own"])
        self.assertIn("annotation budget allocation", CANONICAL["does_not_own"])

    def test_sibling_relationships_do_not_claim_integration(self):
        for edge in CANONICAL["relationships"]:
            self.assertFalse(edge["integration_exercised"])

    def test_capabilities_are_repository_native(self):
        capabilities = set(CAPABILITIES["capabilities"])
        self.assertNotIn("hyper-scaling", capabilities)
        self.assertIn("independent_marginal_chance_baseline", capabilities)
        self.assertIn("pairwise_agreement_lift", capabilities)
        self.assertIn("policy_bound_pair_receipt", capabilities)
        self.assertIn("python_c_statistical_parity", capabilities)

    def test_target_waits_for_exact_head_proof(self):
        self.assertEqual(TARGET["current"]["state"], "PROMOTED")
        self.assertTrue(TARGET["current"]["canonical_position_pending_exact_head_proof"])
        self.assertEqual(TARGET["promotion"]["next_gate"], "CANONICAL_POSITION_RESOLVED")

    def test_truth_boundary_keeps_anomaly_separate_from_misconduct(self):
        boundary = CAPABILITIES["truth_boundary"]
        self.assertIn("not proof of collusion or misconduct", boundary)
        self.assertIn("does not authenticate annotators", boundary)
        self.assertIn("execute labeling jobs", boundary)


if __name__ == "__main__":
    unittest.main()
