import utils.GitHubUtils as GitHubUtils
import utils.JsonUtils as JsonUtils
import warnings

from travispy import TravisPy
# ignore travis package warnings
warnings.filterwarnings("ignore")

# First create a Travis instance using an Github access token
t = TravisPy.github_auth("b43b59e5a8d621516c3653b52b30f3df112a0f11")


def get_travis_status(repository):
    status = False
    r = GitHubUtils.get_slug_git_url(repository)
    try:
        repo = t.repo(r)
        status = repo.active
    except:
        try:
            repo = t.repo(r.lower())
            status = repo.active
        except Exception as e:
            print(r)
            print(e)
    return status


result = []

ds_ufmg = JsonUtils.unpack(JsonUtils.get_data(
    "data/refactorings_ufmg_travis.json"))
ds_kessentini = JsonUtils.unpack(JsonUtils.get_data(
    "data/refactorings_kessentini_travis.json"))

active = 0
i = 1
for item in ds_ufmg:
    item["id_ufmg"] = item["id"]
    item["id"] = i
    item["travis_active"] = get_travis_status(item["repository"])
    result.append(item)

    if item["travis_active"]:
        active += 1

    i += 1

for item in ds_kessentini:
    item["id_ufmg"] = None
    item["id"] = i
    item["travis_active"] = get_travis_status(item["repository"])
    result.append(item)

    if item["travis_active"]:
        active += 1

    i += 1

print("Actives:", active)
print("Items:", i)

JsonUtils.save_data("data/data_refactorings.json", result)
