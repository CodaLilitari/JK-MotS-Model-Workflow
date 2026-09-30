import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contract", ROOT / "skills/jk-mots-model-workflow/scripts/inspect_contract.py")
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


def model(count=3, parents=None):
    parents = parents or [-1] + [0] * (count - 1)
    return "SECTION: HIERARCHYDEF\nHIERARCHY NODES %d\n" % count + "\n".join(
        f"{i}: 0x0 0x1 -1 {parents[i]} -1 -1 0 0 0 0 0 0 0 0 0 0 part{i}" for i in range(count))


def key(joints=3, indices=(0, 1)):
    return f"SECTION: HEADER\nJOINTS {joints}\nSECTION: KEYFRAME NODES\nNODES {len(indices)}\n" + "\n".join(f"NODE {i}\nMESH NAME part{i}\nENTRIES 0" for i in indices)


class ContractTests(unittest.TestCase):
    def check_pair(self, joints=3, references=(), detail=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            m = root / "candidate.3do"
            k = root / "walk.key"
            m.write_text(model())
            k.write_text(key(joints))
            paths = []
            for i, value in enumerate(references):
                p = root / f"ref{i}.key"
                p.write_text(key(value))
                paths.append(p)
            return contract.inspect(m, [k], paths, detail)

    def test_matching_allocation(self):
        self.assertEqual(self.check_pair()["issues"], [])

    def test_padding_contract_is_joint_allocation_not_record_count(self):
        result = self.check_pair(2)
        self.assertEqual(result["issues"][0]["kind"], "allocation_too_small")
        self.assertEqual(result["keys"][0]["node_records"], 2)

    def test_reserved_unanimated_indices_still_matter(self):
        result = self.check_pair(references=(3,), detail=2)
        self.assertEqual(result["issues"][0]["kind"], "detail_overlaps_reserved_domain")

    def test_extra_key_track_can_exist_beyond_stock_model(self):
        with tempfile.TemporaryDirectory() as folder:
            m, k = Path(folder) / "stock.3do", Path(folder) / "idle.key"
            m.write_text(model())
            k.write_text(key(4, (0, 1, 3)))
            result = contract.inspect(m, [k])
            self.assertEqual(result["status"], "checks_passed")
            self.assertEqual(result["observations"][0]["indices"], [3])

    def test_comments_are_not_tracks(self):
        parsed = contract.parse_key(key() + "\n# NODE 99\n")
        self.assertEqual(parsed["track_indices"], [0, 1])

    def test_cycle_refused(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            contract.parse_model(model(parents=[2, 0, 1]))

    def test_duplicate_track_refused(self):
        with self.assertRaises(ValueError):
            contract.parse_key(key(indices=(0, 0)))

    def test_track_outside_allocation_refused(self):
        with self.assertRaises(ValueError):
            contract.parse_key(key(joints=2, indices=(0, 2)))

    def test_negative_track_cannot_hide_behind_zero_nodes(self):
        with self.assertRaisesRegex(ValueError, "negative"):
            contract.parse_key("JOINTS 1\nNODES 0\nNODE -1\n")

    def test_malformed_track_cannot_be_silently_ignored(self):
        with self.assertRaises(ValueError):
            contract.parse_key("JOINTS 1\nNODES 0\nNODE nonsense\n")

    def test_declared_count_mismatch(self):
        with self.assertRaises(ValueError):
            contract.parse_model(model().replace("NODES 3", "NODES 4"))


if __name__ == "__main__":
    unittest.main()
