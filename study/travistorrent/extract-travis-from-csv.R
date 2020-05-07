#code adapted from: https://gitlab.com/rodrigorgs/msr17-challenge/blob/master/src/extract-travis-from-csv.R
# First run: download_snapshot.sh

library(data.table)
library(dplyr)

travis_full <- fread(file = 'travistorrent_8_2_2017.csv')
#travis_full <- fread('zcat data/travistorrent_8_2_2017.csv.gz')
saveRDS(travis_full, 'travistorrent_8_2_2017.rds')

travis <- travis_full %>%
  select(c(gh_lang, gh_project_name, gh_first_commit_created_at, git_branch, git_num_all_built_commits, git_prev_built_commit, git_prev_commit_resolution_status, git_trigger_commit, tr_status, tr_duration, tr_build_id, tr_prev_build, tr_log_num_tests_failed, tr_log_status, tr_original_commit, tr_prev_build))

saveRDS(travis, 'travis.rds')
