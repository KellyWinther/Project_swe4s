import unittest
import pandas as pd
from src/raster_plot import prepare_raster_df

class TestPrepareRasterDF(unittest.TestCase):

    def test_invalid_df_type(self):
        """Raise TypeError for non-DataFrame input."""
        with self.assertRaises(TypeError):
            prepare_raster_df(123)

    def test_missing_required_columns(self):
        """ValueError for missing required columns."""
        df = pd.DataFrame({"Peak": [1.0]})
        with self.assertRaises(ValueError):
            prepare_raster_df(df)

    def test_ripple_index_none_uses_all(self):
        """default ripple_index=None includes all ripples."""
        df = pd.DataFrame({
            "Peak": [1.0, 2.0],
            "Spike Times (s)": [[0.9], [1.9, 2.2]],
            "Cluster IDs": [[10], [11, 12]]
        })

        out = prepare_raster_df(df, ripple_index=None)
        self.assertEqual(len(out), 3)  # 1 spike + 2 spikes

    def test_ripple_index_single_int(self):
        """definied ripple_index extracts exactly one ripple row."""
        df = pd.DataFrame({
            "Peak": [1.0, 2.0],
            "Spike Times (s)": [[0.9, 1.1], [1.9]],
            "Cluster IDs": [[10, 11], [12]]
        })

        out = prepare_raster_df(df, ripple_index=0)

        self.assertEqual(len(out), 2)
        self.assertEqual(float(out["Peak"].unique()[0]), 1.0)

    def test_ripple_index_list_combines(self):
        """List of indices should merge multiple ripples."""
        df = pd.DataFrame({
            "Peak": [1.0, 2.0],
            "Spike Times (s)": [[0.9], [2.0, 2.1]],
            "Cluster IDs": [[10], [11, 11]]
        })

        out = prepare_raster_df(df, ripple_index=[0, 1])
        self.assertEqual(len(out), 3)

    def test_explode_rows(self):
        """List-of-lists should explode into one row per spike."""
        df = pd.DataFrame({
            "Peak": [1.0],
            "Spike Times (s)": [[0.9, 1.05, 1.10]],
            "Cluster IDs": [[10, 11, 10]]
        })

        out = prepare_raster_df(df, ripple_index=0)
        self.assertEqual(len(out), 3)

    def test_t_rel_computation(self):
        """t_rel = spike_time - peak."""
        df = pd.DataFrame({
            "Peak": [1.0],
            "Spike Times (s)": [[0.9, 1.2]],
            "Cluster IDs": [[10, 11]]
        })

        out = prepare_raster_df(df, ripple_index=0)

        self.assertAlmostEqual(out["t_rel"].iloc[0], -0.1)
        self.assertAlmostEqual(out["t_rel"].iloc[1], 0.2)

if __name__ == '__main__':
    unittest.main()
