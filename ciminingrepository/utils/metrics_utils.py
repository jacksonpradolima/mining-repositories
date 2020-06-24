import multiprocessing as mp
import os
import sys

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

