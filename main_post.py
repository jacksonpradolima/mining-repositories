import argparse
import csv
import os

import pandas as pd
from pathlib2 import Path

from ciminingrepository.utils.metrics_utils import apply_post_processing

DEFAULT_EXPERIMENT_DIR = 'results/features_post'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Main - Post Processing')

    ap.add_argument('--feature_dir', required=True)
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

        df = pd.read_csv(f"{args.feature_dir}{os.sep}{system}_features.csv", sep=";")

        apply_post_processing(df)

        df.to_csv(f"{args.output_dir}{os.sep}{system}_features.csv", sep=';',
                  header=True, index=False,
                  quoting=csv.QUOTE_NONE)