import multiprocessing as mp
import os
import sys
from itertools import accumulate

import numpy as np
from metrics.compute import compute_file_metrics
from pygments.lexers import guess_lexer_for_filename


def _process_file_metrics_parallel(root_dir, key, file_metrics, file_processors):
    try:
        in_file = os.path.join(root_dir, key)

        with open(in_file, 'rb') as ifile:
            code = ifile.read()
        # lookup lexicographical scanner to use for this run
        try:
            lex = guess_lexer_for_filename(in_file, code, encoding='guess')
            # encoding is 'guess', chardet', 'utf-8'
        except:
            pass
        else:
            token_list = lex.get_tokens(code)  # parse code
            metrics = compute_file_metrics(file_processors, lex.name, key, token_list)

            # Workaround to use nested dict with multiprocessing
            file_metrics[key] = {
                'sloc': metrics['sloc'],
                'mccabe': metrics['mccabe'],
                'language': lex.name
            }

    except IOError as e:
        sys.stderr.writelines(str(e) + " -- Skipping input file.\n\n")


def process_file_metrics(root_dir, in_file_names, file_processors):
    """Main routine for metrics."""
    manager = mp.Manager()
    file_metrics = manager.dict()

    parameters = [(root_dir, key, file_metrics, file_processors) for key in in_file_names]

    # main loop
    p = mp.Pool(max(1, mp.cpu_count() - 1))
    p.starmap(_process_file_metrics_parallel, parameters)
    p.close()
    p.join()

    return file_metrics


def apply_user_preference(df, percs=[0.1, 0.5, 0.8]):
    # Create the columns
    df['UserPref_80'] = 0
    df['UserPref_50'] = 0
    df['UserPref_10'] = 0

    commits = df["BuildId"].unique().tolist()

    # For each commit
    for commit in commits:
        # Get the failing test cases in current commit
        tc_fails = np.array(df.loc[df['BuildId'] == commit, 'NumErrors'].tolist())

        # If there is a test case that fails
        if sum(tc_fails) > 0:
            # Find the failing test indices
            ii = np.where(tc_fails > 0)[0]

            # For each percentage of user-preference
            for perc in percs:
                # how many positions to choose
                nsamples = int(perc * len(ii))

                # select random positions
                positions = np.random.choice(len(ii), nsamples, replace=False)

                # Reset all values
                tc_fails = np.zeros(len(tc_fails))

                # apply changes
                tc_fails[ii[positions]] = 1

                # We desire integer values
                tc_fails = tc_fails.astype(int)

                # Update the data
                df.loc[df['BuildId'] == commit, f'UserPref_{int(perc * 100)}'] = tc_fails


def apply_test_case_age(df):
    df['TcAge'] = 1

    for tccount, name in enumerate(df.Name.unique(), start=1):
        age = df.loc[df['Name'] == name, 'TcAge'].tolist()

        df.loc[df['Name'] == name, 'TcAge'] = [1] + [sum(age[i::-1]) + 1 for i in range(0, len(age) - 1)]


def apply_post_processing(df):
    """
    This function take a list of numbers and replace all zeros by the previous nonzero value
    Example: [1, 0, 0, 2, 0] -> [1,1,1,2,2]
    :param df:
    :return:
    """
    for tccount, name in enumerate(df.Name.unique(), start=1):
        sloc = df.loc[df['Name'] == name, 'SLOC'].tolist()
        mccabe = df.loc[df['Name'] == name, 'McCabe'].tolist()

        df.loc[df['Name'] == name, 'SLOC'] = list(accumulate(sloc, lambda x, y: y if y else x))
        df.loc[df['Name'] == name, 'McCabe'] = list(accumulate(mccabe, lambda x, y: y if y else x))
