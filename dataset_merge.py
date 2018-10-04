import utils.GitHubUtils as GitHubUtils
import utils.JsonUtils as JsonUtils
import warnings

from travispy import TravisPy
# ignore travis package warnings
warnings.filterwarnings("ignore")

result = []

ds_ufmg = JsonUtils.unpack(JsonUtils.get_data(
    "data/refactorings_ufmg_travis.json"))

ds_kessentini = JsonUtils.unpack(JsonUtils.get_data(
    "data/refactorings_kessentini_travis.json"))

i = 1
for item in ds_ufmg:
    item["id_ufmg"] = item["id"]
    item["id"] = i
    result.append(item)
    i += 1

for item in ds_kessentini:
    item["id_ufmg"] = None
    item["id"] = i
    result.append(item)
    i += 1

JsonUtils.save_data("data/data_refactorings.json", result)
