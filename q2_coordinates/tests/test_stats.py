# ----------------------------------------------------------------------------
# Copyright (c) 2017--, QIIME 2 development team.
#
# Distributed under the terms of the Lesser GPL 3.0 licence.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from .test_coordinates import CoordinatesTestPluginBase
from qiime2.plugins import coordinates
import qiime2
import pandas as pd
import numpy as np
from skbio import DistanceMatrix
import pandas.util.testing as pdt
from q2_coordinates.stats import autocorr_from_dm, match_ids


# these tests make sure the actions run and accept appropriate inputs
class TestStats(CoordinatesTestPluginBase):

    def setUp(self):
        super().setUp()

        self.tmpd = self.temp_dir.name
        dm_fp = self.get_data_path('dm.qza')
        self.dm = qiime2.Artifact.load(dm_fp)
        alpha_fp = self.get_data_path('alpha_diversity.qza')
        alpha = qiime2.Artifact.load(alpha_fp)
        self.alpha = alpha.view(qiime2.Metadata).get_column('observed_otus')

    # does it run
    def test_autocorr(self):
        coordinates.actions.autocorr(
            distance_matrix=self.dm,
            metadata=self.alpha,
            intersect_ids=True)

    def test_autocorr_nonintersecting_ids_warning(self):
        with self.assertRaisesRegex(ValueError, "matrix are missing"):
            coordinates.actions.autocorr(
                distance_matrix=self.dm,
                metadata=self.alpha,
                intersect_ids=False)

    def test_match_ids(self):
        md = pd.Series({'peanuts': [1, 2, 3, 4]})
        distances = [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]]
        dm = DistanceMatrix(distances, ids=['a', 'b', 'c', 'd'])
        with self.assertRaisesRegex(ValueError, "No samples match"):
            match_ids(md, dm, intersect_ids=True)

    def test_autocorr_from_dm(self):
        np.random.seed(124)
        exp = pd.DataFrame(
            {'Moran\'s I':
                [-0.00975936992946, -0.0909090909091, 1.08994430817,
                 0.275737677144],
             'Geary\'s C':
                [0.715863556271, 1.0, -1.32713928249, 0.0922313064718]},
            index=['Test Statistic', 'Expected Value', 'Z norm', 'p norm'])
        distance_matrix = self.dm.view(DistanceMatrix)
        metadata = self.alpha.to_series()
        metadata, distance_matrix = match_ids(
            metadata, distance_matrix, intersect_ids=True)
        print(metadata.index)
        print(distance_matrix.ids)
        results, weights = autocorr_from_dm(
            metadata, distance_matrix, permutations=0,
            two_tailed=True, transformation='R')
        print(exp)
        print(results)
        pdt.assert_frame_equal(results, exp)
