import sys
import unittest
import numpy as np

sys.path.append("src/")  # noqa

import sequence_matching_utils as utils  # noqa


# Default parameters used in 'lccs_rabin_karp'
BASE = 257
MOD = (1 << 61) - 1


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

        # Sanity check for a small number powers
        pow_base = utils._compute_pow_base(
            n=3,
            base=BASE,
            mod=MOD,
        )
        self.assertEqual(
            pow_base, [1, 257, 66049, 16974593],
        )

        # Ensures that all n < 0 return an empty list
        self.assertEqual(
            utils._compute_pow_base(-1, BASE, MOD),
            utils._compute_pow_base(-2, BASE, MOD),
        )

        # Ensures that all n = 0 returns [1]
        self.assertEqual(
            utils._compute_pow_base(0, BASE, MOD),
            [1],
        )

    def test_prefix_hash(self):

        valid_array = [0, 4, 20, 200, 3]

        # Ensures that '_prefix_hash' works with lists and np.arrays
        self.assertTrue(
            utils._prefix_hash(valid_array, BASE, MOD),
            utils._prefix_hash(np.array(valid_array), BASE, MOD),
        )

        # Ensures that an empty list does return a hash (0)
        self.assertEqual(utils._prefix_hash([], BASE, MOD), [0])

    def test_lccs_rabin_karp(self):

        # Overlap of 4 entries [1, 2, 3, 4]
        l1 = [0, 0, 1, 2, 3, 4, 0, 0]
        l2 = [1, 2, 3, 4, 5]

        # Sanity check for a valid call
        overlap, sequence = utils.lccs_rabin_karp(
            l1=l1, l2=l2, normalize=True, return_sequence=True,
        )
        self.assertEqual(overlap, 0.8)
        self.assertEqual(sequence, [1, 2, 3, 4])

        # Ensures that 'return_sequence' behaves as expected
        overlap = utils.lccs_rabin_karp(
            l1=l1, l2=l2, normalize=True, return_sequence=False,
        )
        self.assertEqual(overlap, 0.8)

        # Checks that 'normalize=False' works as intended
        overlap = utils.lccs_rabin_karp(
            l1=l1, l2=l2, normalize=False, return_sequence=False,
        )
        self.assertEqual(overlap, 4)


if __name__ == "__main__":
    unittest.main()
