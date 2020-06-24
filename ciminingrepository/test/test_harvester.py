import unittest
import os
import csv

import pandas as pd

from ciminingrepository.harvester import Harvester


class RunningHarvester(unittest.TestCase):
    def setUp(self):
        self.dataset_dir = "../../data"
        self.slug = "alibaba@druid"

    def test_commits(self):
        df = pd.read_csv(f"{self.dataset_dir}{os.sep}{self.slug}{os.sep}data-filtered.csv", sep=";")

        # ['build_id', 'build', 'commit', 'travis_started_at', 'log_status',
        # 'tc_id', 'tc_name', 'tc_duration', 'tc_run', 'tc_failed'],

        # print(df.columns)
        # df = df[['commit', 'tc_name', 'tc_duration', 'tc_run', 'tc_failed']]

        # Filter to test
        # df = df[df.commit.isin(commits)]

        commits = df["commit"].unique().tolist()

        commits = commits[:10]
        # commits = ['f27d3595e6adf8353fa355c75e92f526ca442303',
        #           '556f8a76d4ca2c8edda75a29974d3413686d09cc']

        test_cases = df["tc_name"].unique().tolist()

        # Prepare the mining (and cloning the repo)
        h = Harvester(self.slug.replace("@", "/"), commits, "D:\druid")

        r = h.get_features(test_cases)

        # to guarantee the right merge
        df['tc_name_lower'] = df['tc_name'].str.lower()
        r['tc_name_lower'] = r['tc_name'].str.lower()

        r = r[['commit', 'tc_name_lower', 'sloc', 'mccabe', 'change_type']]

        df = pd.merge(df, r, on=['commit', 'tc_name_lower'], how='left')

        df.drop('tc_name_lower', axis=1, inplace=True)

        df['tc_age'] = 1

        for tccount, name in enumerate(df.tc_name.unique(), start=1):
            verdicts = df.loc[df['tc_name'] == name, 'tc_age'].tolist()

            df.loc[df['tc_name'] == name, 'tc_age'] = [1] + [sum(verdicts[i::-1])+1 for i in
                                                                range(0, len(verdicts) - 1)]

        df.sloc.fillna(0, inplace=True)
        df.mccabe.fillna(0, inplace=True)
        df.change_type.fillna(6, inplace=True)

        df.to_csv(f"druid_features.csv", sep=';',
                  header=True, index=False,
                  quoting=csv.QUOTE_NONE)
