import unittest
#import analysis_utils
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import loading_utils
import random
from pathlib import Path
BASE = Path(__file__).parent.parent


# class TestAnalysisUtils(unittest.TestCase):
#     def test_make_cor_dict_no_dat(self):
#         filename = "test/test_data/no_dat.csv"
#         data = 
#         expected_mean = 3.0
#         self.assertEqual(analysis_utils.calculate_mean(data), expected_mean)

#     def test_calculate_median(self):
#         data = [3, 1, 4, 2, 5]
#         expected_median = 3
#         self.assertEqual(analysis_utils.calculate_median(data), expected_median)

#     def test_calculate_mode(self):
#         data = [1, 2, 2, 3, 4]
#         expected_mode = 2
#         self.assertEqual(analysis_utils.calculate_mode(data), expected_mode)

class TestloadingUtils(unittest.TestCase):
    def test_load_spike_dat_none(self):
        timename = BASE / "test" / "test_data" / "empty.npy"
        clustername = BASE / "test" / "test_data" / "empty_clusters.npy"
        labelname = BASE / "test" / "test_data" / "empty_labels.tsv"
        with self.assertRaises(FileNotFoundError):
            loading_utils.load_spike_data(timename, clustername, labelname)
        


    # def test_load_spike_dat(self):
    #     timename = BASE / "test" / "test_data" / "test_spike_times_int.npy"
    #     clustername = BASE / "test" / "test_data" / "test_spike_clusters_int.npy"
    #     labelname = BASE / "test" / "test_data" / "test_cluster_KSLabel_int.tsv"
    #     data = loading_utils.load_spike_data(timename, clustername, labelname)
    #     self.assertIsNotNone(data)
    #     # self.assertIn('time', data.columns)
    #     # self.assertIn('cluster_id', data.columns)
    #     # self.assertIn('KSLabel', data.columns)
    
    def test_is_time_in_range(self):
        self.assertTrue(loading_utils.time_in_range(0, 10, 5))
        self.assertFalse(loading_utils.time_in_range(0, 10, -1))
        self.assertFalse(loading_utils.time_in_range(0, 10, 11))

    # def test_match_times_progress_good(self):
    #     timename = "test/test_data/test_spike_times_int.npy"
    #     clustername = "test/test_data/test_spike_clusters_int.npy"
    #     labelname = "test/test_data/test_cluster_KSLabel_int.tsv"
    #     swr_dir = "test/test_data/test_SWRs_int.csv"
    #     df = loading_utils.load_spike_data(timename, clustername, labelname)
    #     data = loading_utils.match_times(df, swr_dir, True, True)
    #     expected_data = data # Replace with actual expected data if available
    #     self.assertEqual(data, expected_data)

    # def test_match_times_no_progress_no_good(self):
    #     timename = "test/test_data/test_spike_times_int.npy"
    #     clustername = "test/test_data/test_spike_clusters_int.npy"
    #     labelname = "test/test_data/test_cluster_KSLabel_int.tsv"
    #     swr_dir = "test/test_data/test_SWRs_int.csv"
    #     df = loading_utils.load_spike_data(timename, clustername, labelname)
    #     data = loading_utils.match_times(df, swr_dir, False, False)
    #     expected_data = data # Replace with actual expected data if available
    #     self.assertEqual(data, expected_data)

    
if __name__ == '__main__':
    unittest.main()