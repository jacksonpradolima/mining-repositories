import csv
import os
import unittest

import numpy as np
import pandas as pd

from ciminingrepository.harvester import Harvester
from ciminingrepository.utils.metrics_utils import apply_user_preference

class RunningHarvester(unittest.TestCase):
    def setUp(self):
        self.dataset_dir = "../../data"
        self.slug = "alibaba@druid"
        self.df = pd.read_csv(f"{self.dataset_dir}{os.sep}{self.slug}{os.sep}data-filtered.csv", sep=";")

    @unittest.skip
    def test_commits(self):
        # ['build_id', 'build', 'commit', 'travis_started_at', 'log_status',
        # 'tc_id', 'tc_name', 'tc_duration', 'tc_run', 'tc_failed'],

        # print(df.columns)
        # df = df[['commit', 'tc_name', 'tc_duration', 'tc_run', 'tc_failed']]

        # Filter to test
        # df = df[df.commit.isin(commits)]

        commits = self.df["commit"].unique().tolist()

        commits = commits[:10]
        # commits = ['f27d3595e6adf8353fa355c75e92f526ca442303',
        #           '556f8a76d4ca2c8edda75a29974d3413686d09cc']

        test_cases = self.df["tc_name"].unique().tolist()

        # Prepare the mining (and cloning the repo)
        h = Harvester(self.slug.replace("@", "/"), commits, "D:\druid")

        r = h.get_features(test_cases)

        # to guarantee the right merge
        self.df['tc_name_lower'] = self.df['tc_name'].str.lower()
        r['tc_name_lower'] = r['tc_name'].str.lower()

        r = r[['commit', 'tc_name_lower', 'sloc', 'mccabe', 'change_type']]

        self.df = pd.merge(self.df, r, on=['commit', 'tc_name_lower'], how='left')

        self.df.drop('tc_name_lower', axis=1, inplace=True)

        self.df['tc_age'] = 1

        for tccount, name in enumerate(self.df.tc_name.unique(), start=1):
            verdicts = self.df.loc[self.df['tc_name'] == name, 'tc_age'].tolist()

            self.df.loc[self.df['tc_name'] == name, 'tc_age'] = [1] + [sum(verdicts[i::-1]) + 1 for i in
                                                                       range(0, len(verdicts) - 1)]

        self.df.sloc.fillna(0, inplace=True)
        self.df.mccabe.fillna(0, inplace=True)
        self.df.change_type.fillna(6, inplace=True)

        self.df.to_csv(f"druid_features.csv", sep=';',
                       header=True, index=False,
                       quoting=csv.QUOTE_NONE)


    def test_user_preferece(self):
        df = self.df.copy()

        apply_user_preference(df)

        df.to_csv(f"druid_features_perc.csv", sep=';',
                  header=True, index=False,
                  quoting=csv.QUOTE_NONE)
