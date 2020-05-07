from pydriller import RepositoryMining

repository = '/mnt/NAS/japlima/mining-repositories/gits/DSpace/'

# only commits that modified java files
java_commits = RepositoryMining(repository, only_modifications_with_file_types=[
                                '.java']).traverse_commits()

count = 0
# limit 20
# java_commits = list(java_commits)[:20]

print("====================\nCommit info: ")
for commit in java_commits:
    count += 1
    print('Hash {} authored by {} includes {} modified files: {}'.format(commit.hash, commit.author.name, len(commit.modifications),
                                                                         ', '.join(mod.filename for mod in commit.modifications)))

    if count >= 1:
        break

count = 0
print("\n====================\nDiff files: ")
# Diff of files
for commit in java_commits:
    count += 1
    for modification in commit.modifications:
        print('Filename {}'.format(modification.filename))
        print('Diff: {}'.format(modification.diff))
    if count >= 1:
        break

print("\n====================\nCommits containing bugs in message: ")
# commits_containing_bugs_in_message
count = 0
for commit in java_commits:
    count += 1
    if 'bug' in commit.msg:
        print('Commit {} fixed a bug: {}'.format(commit.hash, commit.msg))
        count += 1
    if count >= 20:
        break
