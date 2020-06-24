import os
import shutil
import stat
import tempfile
from typing import List

import pandas as pd
from git import Repo
from metrics.mccabe import McCabeMetric
from metrics.plugins import load_plugins
from metrics.sloc import SLOCMetric
from pathlib2 import Path
from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType

from ciminingrepository.utils.github_utils import auth_gh
from ciminingrepository.utils.metrics_utils import process_file_metrics

pd.set_option('display.max_columns', None)


class Harvester(object):
    def __init__(self, slug, commits: List[str], local_repo=None):
        self.slug = slug
        self.url_repository = f"https://github.com/{self.slug}.git"

        self.gh = auth_gh()
        self.repository = self.gh.get_repo(self.slug)

        self.commits_sha = commits

        self.stream_repo = True if local_repo is None else False

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
        if self.stream_repo:
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

        context = {
            'root_dir': self.local_path_repo,
            'in_file_names': in_file_names,
            'last_metrics': {}
        }

        file_processors, build_processors = load_plugins()
        file_processors = [SLOCMetric(context), McCabeMetric(context)] + [p(context) for p in file_processors]

        file_metrics = process_file_metrics(self.local_path_repo, in_file_names, file_processors)

        df = self.df_format(file_metrics)
        return df[['path_to_file', 'tc_name', 'sloc', 'mccabe']]

    def get_features(self, test_cases):
        df = pd.DataFrame(columns=['commit', 'path_to_file', 'tc_name', 'sloc', 'mccabe', 'change_type'])

        try:
            # Load the repository
            repo = Repo(self.local_path_repo, search_parent_directories=True)

            # Load information from PyDriller
            java_commits = self.get_repo_mining()

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
        finally:
            self._delete_temp_folder()

        return df
