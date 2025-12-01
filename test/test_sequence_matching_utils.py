import sys
import unittest
import numpy as np

sys.path.append("src/")  # noqa

import sequence_matching_utils as utils # noqa


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


if __name__ == "__main__":
    unittest.main()
