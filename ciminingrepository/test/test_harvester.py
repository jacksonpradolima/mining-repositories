import csv
import os
import unittest

import pandas as pd

from ciminingrepository.harvester import Harvester
from ciminingrepository.utils.metrics_utils import apply_user_preference, apply_test_case_age
from ciminingrepository.data_filtering import feature_engineering_contextual

class RunningHarvester(unittest.TestCase):
    def setUp(self):
        self.dataset = "alibaba@druid"
        # self.dataset = "DSpace@DSpace"
        # self.dataset = "square@okhttp"
        # self.dataset = "square@retrofit"
        # self.dataset = "zxing@zxing"
        # self.dataset = "google@guava"
        # self.dataset = "deeplearning4j@deeplearning4j"
        self.clone_dir = "D:\github-datasets"
        self.output_dir = "../../results/test"
        self.dataset_dir = "D:\mab-datasets"
        self.df = pd.read_csv(f"{self.dataset_dir}{os.sep}{self.dataset}{os.sep}data-filtered.csv", sep=";")

    def test_commits(self):
        slug = self.dataset.replace("@", "/")
        system = slug.split("/")[-1]

        commits = self.df["commit"].unique().tolist()
        test_cases = self.df["tc_name"].unique().tolist()

        #commits = commits[:2]

        self.df = self.df[self.df.commit.isin(commits)]

        # Prepare the mining (and cloning the repo)
        h = Harvester(slug, commits, os.path.join(self.clone_dir, system))

        r = h.get_features(test_cases)

        # to guarantee the right merge
        self.df['tc_name_lower'] = self.df['tc_name'].str.lower()
        r['tc_name_lower'] = r['tc_name'].str.lower()

        r = r[['commit', 'tc_name_lower', 'sloc', 'mccabe', 'change_type']]

        self.df = self.df.merge(r, on=['commit', 'tc_name_lower'], how='left')

        self.df.drop('tc_name_lower', axis=1, inplace=True)

        self.df.sloc.fillna(0, inplace=True)
        self.df.mccabe.fillna(0, inplace=True)
        self.df.change_type.fillna(6, inplace=True)

        self.df = feature_engineering_contextual(self.df)
        apply_test_case_age(self.df)
        apply_user_preference(self.df)

        self.df.to_csv(f"{self.output_dir}{os.sep}{system}_features.csv", sep=';',
                       header=True, index=False,
                       quoting=csv.QUOTE_NONE)

    @unittest.skip
    def test_user_preferece(self):
        df = self.df.copy()

        apply_user_preference(df)

        df.to_csv(f"druid_features_perc.csv", sep=';',
                  header=True, index=False,
                  quoting=csv.QUOTE_NONE)
