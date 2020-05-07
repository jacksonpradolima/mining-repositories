import utils.GitHubUtils as GitHubUtils
import utils.JsonUtils as JsonUtils
import utils.TravisUtils as TravisUtils

# Get the dataset in json format
dataset = JsonUtils.get_data("data/refactorings.json")

# Filter unique repositories
repos = set([GitHubUtils.get_slug_git_url(x.repository) for x in dataset])

# Filter the repositories that contains Travis CI
repos_travis = [x for x in repos if GitHubUtils.is_travis_project(
    x) and TravisUtils.is_active(x)]

# Filter refactorings where the repositoris contains Travis CI
dataset_travis = [x for x in dataset if GitHubUtils.get_slug_git_url(
    x.repository) in repos_travis]

JsonUtils.save_data("data/refactorings_ufmg_travis.json", dataset_travis)
