import sys
import unittest
import numpy as np

sys.path.append("src/")  # noqa

import sequence_matching_utils as utils  # noqa


class TestHashUtils(unittest.TestCase):
    def test_preprocess_lists(self):

        for _ in range(20):

            # Two lists with random lengths & random int values
            original_l1 = np.random.uniform(
                low=0,
                high=10,
                size=np.random.randint(low=1, high=5)
            ).astype(int)
            original_l2 = np.random.uniform(
                low=0,
                high=10,
                size=np.random.randint(low=1, high=5)
            ).astype(int)

            l1, l2 = utils._preprocess_lists(
                original_l1,
                original_l2,
            )

            # Checks that _preprocess_lists() reorders lists correctly
            self.assertTrue(
                len(l1) <= len(l2)
            )

    def test_compute_pow_base(self):

        # Default parameters used in 'lccs_rabin_karp'
        base = 257
        mod = (1 << 61) - 1

        # Sanity check for a small number powers
        pow_base = utils._compute_pow_base(
            n=3,
            base=base,
            mod=mod,
        )
        self.assertEqual(
            pow_base, [1, 257, 66049, 16974593],
        )

        # Ensures that all n < 0 return an empty list
        self.assertEqual(
            utils._compute_pow_base(-1, base, mod),
            utils._compute_pow_base(-2, base, mod),
        )

        # Ensures that all n = 0 returns [1]
        self.assertEqual(
            utils._compute_pow_base(0, base, mod),
            [1],
        )

    def test_prefix_hash(self):
        pass

    def test_get_hash(self):
        pass

    def test_has_match(self):
        pass

    def test_recover_sequence(self):
        pass

    def test_lccs_rabin_karp(self):
        pass


if __name__ == "__main__":
    unittest.main()
