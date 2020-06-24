import os
import shutil
import stat
import tempfile
# from pathlib import Path
from typing import List
from collections import OrderedDict
from pygments.lexers import guess_lexer_for_filename
from pathlib2 import PurePath, Path

import multiprocessing as mp
import sys
import pathspec

import pandas as pd
from git import Repo
from metrics.mccabe import McCabeMetric
# from metrics.metrics_utils import process_file_metrics
from metrics.plugins import load_plugins
from metrics.position import PosMetric
from metrics.sloc import SLOCMetric
from metrics.compute import compute_file_metrics
from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType

from ciminingrepository.utils.github_utils import auth_gh

pd.set_option('display.max_columns', None)


class Harvester(object):
    def __init__(self, slug, commits: List[str], local_repo=None):
        self.slug = slug
        self.url_repository = f"https://github.com/{self.slug}.git"

        self.gh = auth_gh()
        self.repository = self.gh.get_repo(self.slug)

        self.commits_sha = commits

        self.local_path_repo = self._clone_remote_repo() if local_repo is None else local_repo

        self.repository_mining = None
        self.update_repo_mining()

    def _clone_remote_repo(self) -> str:
        # Save the temporary directory so we can clean it up later
        self._tmp_dir = tempfile.TemporaryDirectory()

        repo_folder = os.path.join(self._tmp_dir.name, self.slug.split("/")[-1])

        print(f"Cloning {self.slug} in temporary folder {repo_folder}")

        Repo.clone_from(url=self.url_repository, to_path=repo_folder)

        return repo_folder

    def _delete_temp_folder(self):
        # delete the temporary directory if created
        try:
            self._tmp_dir.cleanup()
        except PermissionError:
            # on Windows, Python 3.5, 3.6, 3.7 are not able to delete
            # git directories because of read-only files. This is now fixed
            # in python 3.8. In this case, we need to use an
            # onerror callback to clear the read-only bit.
            # see https://docs.python.org/3/library/shutil.html?highlight=shutil#rmtree-example
            def remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                func(path)

            shutil.rmtree(self._tmp_dir.name, onerror=remove_readonly)

    def update_harvester_repo(self, slug, commits):
        self.slug = slug
        self.repository = self.gh.get_repo(self.slug)
        self.url_repository = f"https://github.com/{self.slug}.git"
        self.commits_sha = commits

        self.update_repo_mining()

    def update_repo_mining(self):
        self.repository_mining = RepositoryMining(self.local_path_repo,
                                                  only_commits=self.commits_sha, include_refs=True).traverse_commits()

    def get_repo_mining(self):
        return self.repository_mining

    def _get_class_file_from_java_path(self, path):
        return path.replace("\\", '.').replace("/", '.').replace('.java', '').replace('src.test.', '')

    def _get_modifications(self, commit, test_cases):
        records = []
        for modification in commit.modifications:
            path = modification.new_path if modification.new_path is not None else modification.old_path

            if path is not None:
                if not path.endswith('.java'):
                    path += '.java'

                if self._get_class_file_from_java_path(path).endswith(tuple(test_cases)):
                    records.append([path, modification.change_type.value])

        return pd.DataFrame(records, columns=['path_to_file', 'change_type'])

    def get_test_case_status(self, test_cases):
        """
        PyDriller

        - Test Case Change (TCC): Considers whether a test case changed. If a test case is changed from a
        commit to another, there is a high probability that the alteration was performed because some change
        in the software needs to be tested. If the test case was changed, we could detect and consider
        if the test case was renamed, or it added or removed some methods;

        """
        java_commits = self.get_repo_mining()

        records = []
        for commit in java_commits:
            for modification in commit.modifications:
                path = modification.new_path if modification.new_path is not None else modification.old_path

                if path is not None:
                    if not path.endswith('.java'):
                        path += '.java'

                    class_file = self._get_class_file_from_java_path(path)

                    if class_file.endswith(tuple(test_cases)):
                        records.append([commit.hash, path, class_file, modification.change_type.value])

        return pd.DataFrame(records, columns=['commit', 'path_to_file', 'test_case', 'change_type'])

    def path_leaf(self, path):
        head, tail = os.path.split(path)
        return tail or os.basename(head)

    def df_format(self, file_metrics):
        def report_header(fmetrics):
            """
            'path_to_file', 'filename', 'sloc', 'comments', 'ratio_comment_to_code', 'mccabe', 'language'
            :param fmetrics:
            :return:
            """
            values = list(fmetrics.values())[0]
            values.pop('block_positions', None)
            # Workaround :D
            return ['path_to_file', 'filename'] + ','.join(values).split(",")

        def report_metrics(fmetrics):
            report = []
            for key, values in fmetrics.items():
                # New row
                row = []
                row.append(key)
                row = row + [str(v) for k, v in values.items()
                             if k not in ['block_positions']]

                row.insert(1, self.path_leaf(row[0]))
                report.append(row)

            return report

        df = pd.DataFrame(report_metrics(file_metrics), columns=report_header(file_metrics))
        df['tc_name'] = df['path_to_file'].apply(lambda x: self._get_class_file_from_java_path(x))

        return df

    def list_paths(self, root_tree, path=Path(".")):
        for blob in root_tree.blobs:
            yield path / blob.name
        for tree in root_tree.trees:
            yield from self.list_paths(tree, path / tree.name)

    # based on: https://github.com/finklabs/botodeploy/blob/master/botodeploy/utils_static.py
    def glob_files(self, root_dir, includes=None, excludes=None, gitignore=None):
        """Powerful and flexible utility to search and tag files using patterns.
        :param root_dir: directory where we start the search
        :param includes: list or iterator of include pattern tuples (pattern, tag)
        :param excludes: list or iterator of exclude patterns
        :param gitignore: list of ignore patterns (gitwildcard format)
        :return: iterator of (absolute_path, relative_path)
        """
        # docu here: https://docs.python.org/3/library/pathlib.html
        if not includes:
            includes = ['**']
        else:
            # we need to iterate multiple times (iterator safeguard)
            includes = list(includes)

        if excludes:
            # we need to iterate multiple times (iterator safeguard)
            excludes = list(excludes)

        if gitignore:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore)
            # log.debug('gitignore patterns: %s', gitignore)

        while includes:
            pattern = includes.pop(0)
            # for compatibility with std. python Lib/glop.py:
            # >>>If recursive is true, the pattern '**' will match any files and
            #    zero or more directories and subdirectories.<<<
            if pattern.endswith('**'):
                pattern += '/*'
            matches = list(Path(root_dir).glob(pattern))

            for m in matches:
                if m.is_dir():
                    continue

                # some discussion on how to convert a pattern into regex:
                # http://stackoverflow.com/questions/27726545/python-glob-but-against-a-list-of-strings-rather-than-the-filesystem
                pp = PurePath(m)

                # check if m is contained in remaining include patterns
                # (last one wins)
                if includes and any(map(lambda p: pp.match(p), includes)):
                    continue

                # check if m is contained in exclude pattern
                if excludes and any(map(lambda p: pp.match(p), excludes)):
                    continue

                # check if m is contained in finkignore
                if gitignore and spec.match_file(str(m)):
                    # log.debug('Skipped file \'%s\' due to gitignore pattern',
                    # str(m.relative_to(root_dir)))
                    continue

                yield (str(m), str(m.relative_to(root_dir)))

    def process_file_metrics(self, root_dir, in_file_names, file_processors):
        """Main routine for metrics."""
        file_metrics = OrderedDict()

        # main loop
        for key in in_file_names:
            in_file = os.path.join(root_dir, key)
            # print 'file %i: %s' % (i, in_file)
            try:
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

                    file_metrics[key] = OrderedDict()
                    file_metrics[key].update(compute_file_metrics(file_processors, lex.name, key, token_list))
                    file_metrics[key]['language'] = lex.name

            except IOError as e:
                sys.stderr.writelines(str(e) + " -- Skipping input file.\n\n")

        return file_metrics

    def get_metrics(self, test_cases, repo, hash):
        """
         This function aims to extract the following data:

         - Cyclomatic Complexity (CC): This feature considers the complexity of McCabe.
         High complexity can be related to a more elaborated test case;

         - Test Size (TS): Typically, size of a test case refers to either the lines of code or
         the number of ``assertions'' in a test case.

         """

        # Checkout the commit (to obtain metrics over files)
        # PyDriller do not support to observe the files in a commit
        repo.git.checkout(hash)

        # Get the commit
        commit = repo.commit(hash)
        in_file_names = []

        # Find the files that we will obtain the metrics
        for path in self.list_paths(commit.tree):
            filename = str(path)

            # if the file is a java file
            # and if it is a test file (checking in the entire path/file name)
            if filename.endswith(".java") and "test" in filename.lower():
                class_file = self._get_class_file_from_java_path(filename)

                if class_file.endswith(tuple(test_cases)):
                    in_file_names.append(filename)

        # TODO: remove after tests
        # in_file_names = in_file_names[:2]

        context = {
            'root_dir': self.local_path_repo,
            'in_file_names': in_file_names,
            'last_metrics': {}
        }

        file_processors, build_processors = load_plugins()
        file_processors = \
            [SLOCMetric(context), McCabeMetric(context), PosMetric(context)] + \
            [p(context) for p in file_processors]

        file_metrics = self.process_file_metrics(self.local_path_repo, in_file_names, file_processors)

        df = self.df_format(file_metrics)
        return df[['path_to_file', 'tc_name', 'sloc', 'mccabe']]

    def get_features(self, test_cases):
        # Load the repository
        repo = Repo(self.local_path_repo, search_parent_directories=True)

        # Load information from PyDriller
        java_commits = self.get_repo_mining()

        df = pd.DataFrame(columns=['commit', 'path_to_file', 'tc_name', 'sloc', 'mccabe', 'change_type'])

        # Now, we iterate over commits under analysis to obtain the features from each test case
        for c in java_commits:
            # Get the test cases that were changed (using PyDriller)
            df_mod = self._get_modifications(c, test_cases)

            # We do this because PyDriller focus on changes, and we desire all information in each commit
            # For example, we have information from valid CI Cycles but we do not know in each commit they are valid.
            # So, we try to get such informations manually
            df_metrics = self.get_metrics(test_cases, repo, c.hash)

            # Default value for all test cases
            df_metrics['change_type'] = ModificationType.UNKNOWN.value

            # Update only the tests that changed
            df_metrics['change_type'] = df_metrics.apply(
                lambda x:
                df_mod.loc[df_mod.path_to_file.str.lower() == x.path_to_file.lower(), 'change_type'].values[0]
                if len(
                    df_mod.loc[df_mod.path_to_file.str.lower() == x.path_to_file.lower(), 'change_type'].values) > 0
                else x['change_type'], axis=1)

            # Update with the current commit
            df_metrics['commit'] = c.hash

            # Add to df with information from all commits
            df = df.append(df_metrics)

        return df
