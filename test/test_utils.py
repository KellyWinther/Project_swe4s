import unittest
from pathlib import Path
import sys
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE / "src"))

import loading_utils # noqa: E402
import analysis_utils # noqa: E402


class TestMakeCorrelationDictionary(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "Cluster IDs": [
                    [1, 2],
                    [2, 3],
                    [1, 3],
                    [1],
                ]
            }
        )

    def test_normalized_correlation(self):
        corr = analysis_utils.make_correlation_dictionary(
            self.df, id_column_name="Cluster IDs", normalize=True
        )

        # Expected:
        # baseline 1: with (1,2,3) => (3,1,1) / 3 = (1.0, 1/3, 1/3)
        self.assertAlmostEqual(corr[1][1], 1.0, places=7)
        self.assertAlmostEqual(corr[1][2], 1.0 / 3.0, places=7)
        self.assertAlmostEqual(corr[1][3], 1.0 / 3.0, places=7)

        # baseline 2: with (1,2,3) => (1,2,1) / 2 = (0.5, 1.0, 0.5)
        self.assertAlmostEqual(corr[2][1], 0.5, places=7)
        self.assertAlmostEqual(corr[2][2], 1.0, places=7)
        self.assertAlmostEqual(corr[2][3], 0.5, places=7)

        # baseline 3: with (1,2,3) => (1,1,2) / 2 = (0.5, 0.5, 1.0)
        self.assertAlmostEqual(corr[3][1], 0.5, places=7)
        self.assertAlmostEqual(corr[3][2], 0.5, places=7)
        self.assertAlmostEqual(corr[3][3], 1.0, places=7)

    def test_raw_counts_when_not_normalized(self):
        corr = analysis_utils.make_correlation_dictionary(
            self.df, id_column_name="Cluster IDs", normalize=False
        )

        # Raw counts expected:
        # baseline 1: self=3, with2=1, with3=1
        self.assertEqual(corr[1][1], 3)
        self.assertEqual(corr[1][2], 1)
        self.assertEqual(corr[1][3], 1)

        # baseline 2: self=2, with1=1, with3=1
        self.assertEqual(corr[2][2], 2)
        self.assertEqual(corr[2][1], 1)
        self.assertEqual(corr[2][3], 1)

        # baseline 3: self=2, with1=1, with2=1
        self.assertEqual(corr[3][3], 2)
        self.assertEqual(corr[3][1], 1)
        self.assertEqual(corr[3][2], 1)


class TestLoadingUtils(unittest.TestCase):
    def test_load_spike_dat_none(self):
        timename = BASE / "data" / "test_data" / "does_not_exist_times.npy"
        clustername = BASE / "data" / "test_data" / "does_not_exist_clusters.npy"
        labelname = BASE / "data" / "test_data" / "does_not_exist_labels.tsv"
        with self.assertRaises(SystemExit):
            loading_utils.load_spike_data(timename, clustername, labelname)

    def test_load_spike_dat(self):
        timename = BASE / "data" / "test_data" / "test_spike_times_int.npy"
        clustername = BASE / "data" / "test_data" / "test_spike_clusters_int.npy"
        labelname = BASE / "data" / "test_data" / "test_cluster_KSLabel_int.tsv"
        df = loading_utils.load_spike_data(timename, clustername, labelname)
        self.assertIsNotNone(df)

    def test_is_time_in_range(self):
        self.assertTrue(loading_utils.time_in_range(0, 10, 5))
        self.assertFalse(loading_utils.time_in_range(0, 10, -1))
        self.assertFalse(loading_utils.time_in_range(0, 10, 11))

    def test_match_times_progress_good(self):
        timename = BASE / "data" / "test_data" / "test_spike_times_int.npy"
        clustername = BASE / "data" / "test_data" / "test_spike_clusters_int.npy"
        labelname = BASE / "data" / "test_data" / "test_cluster_KSLabel_int.tsv"
        df = loading_utils.load_spike_data(timename, clustername, labelname)
        self.assertIsNotNone(df)


if __name__ == "__main__":
    unittest.main()
