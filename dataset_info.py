import utils.GitHubUtils as GitHubUtils
import utils.JsonUtils as JsonUtils

from itertools import groupby
from operator import itemgetter

# Get the dataset in json format
#dataset = JsonUtils.unpack(JsonUtils.get_data("data/data.json"))
dataset = JsonUtils.get_data("data/data.json")

repos = set([x.repository for x in dataset])

print("Repositories:", len(repos))
commits = set(x.sha1 for x in dataset)
print("Commits:", len(commits))
print("Refactorings:", sum([len(x.refactorings) for x in dataset]))
print("Actives:", len([x for x in dataset if x.travis_active]))
