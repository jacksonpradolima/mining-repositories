import argparse
import csv
import os

import pandas as pd
from pathlib2 import Path

from ciminingrepository.harvester import Harvester
from ciminingrepository.utils.metrics_utils import apply_user_preference, apply_test_case_age
from ciminingrepository.data_filtering import feature_engineering_contextual

DEFAULT_EXPERIMENT_DIR = 'results/features/'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Main')

    ap.add_argument('--project_dir', required=True)
    ap.add_argument('--clone_dir', required=True)

    ap.add_argument('--datasets', nargs='+', default=[], required=True,
                    help='Datasets to analyse. Ex: \'deeplearning4j@deeplearning4j\'')

    ap.add_argument('-o', '--output_dir',
                    default=DEFAULT_EXPERIMENT_DIR,
                    const=DEFAULT_EXPERIMENT_DIR,
                    nargs='?')

    args = ap.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    for dataset in args.datasets:
        slug = dataset.replace("@", "/")
        system = slug.split("/")[-1]
        print("Running for", dataset)

        df = pd.read_csv(f"{args.project_dir}{os.sep}{dataset}{os.sep}data-filtered.csv", sep=";")

        commits = df["commit"].unique().tolist()
        test_cases = df["tc_name"].unique().tolist()

        # Prepare the mining (and cloning the repo)
        h = Harvester(slug, commits, os.path.join(args.clone_dir, system))

        # Get the features
        r = h.get_features(test_cases)

        # to guarantee the right merge
        df['tc_name_lower'] = df['tc_name'].str.lower()
        r['tc_name_lower'] = r['tc_name'].str.lower()

        r = r[['commit', 'tc_name_lower', 'sloc', 'mccabe', 'change_type']]

        df = pd.merge(df, r, on=['commit', 'tc_name_lower'], how='left')

        df.drop('tc_name_lower', axis=1, inplace=True)

        df.sloc.fillna(0, inplace=True)
        df.mccabe.fillna(0, inplace=True)
        df.change_type.fillna(6, inplace=True)

        df = feature_engineering_contextual(df)
        apply_test_case_age(df)
        apply_user_preference(df)

        df.to_csv(f"{args.output_dir}{system}_features.csv", sep=';',
                  header=True, index=False,
                  quoting=csv.QUOTE_NONE)
