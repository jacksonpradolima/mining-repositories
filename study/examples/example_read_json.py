import json

from collections import namedtuple


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)


#####################################################
result = []
json_dict = {}
data = []

# for k, v in dic.iteritems():
tmp_dict = {}
tmp_dict["type"] = "Inline Method"
tmp_dict["description"] = "<b>Inline Method</b> <code>public getLanguage(id SLanguageId, langName String, version int) : SLanguage</code> inlined to <code>public getLanguage(id SLanguageId, langName String) : SLanguage</code> in class <code>jetbrains.mps.smodel.adapter.structure.MetaAdapterFactory</code>"
data.append(tmp_dict)


# example
json_dict["id"] = 1105075
json_dict["repository"] = "https://github.com/JetBrains/MPS.git"
json_dict["sha1"] = "2bcd05a827ead109a56cb1f79a83dcd332f42888"
json_dict["author"] = "Mihail Muhin"
json_dict["time"] = "6/7/15 7:36 PM"
json_dict["refactorings"] = data

result.append(json_dict)

with open('data/data.json', 'w') as outfile:
    json.dump(result, outfile, indent=4)


#####################################################
distros_dict = []

with open('data/data.json', 'r') as f:
    distros_dict = json2obj(f.read().replace('\n', ''))

print(distros_dict[0].refactorings[0].type)


distros_dict = []

with open('data/refactorings.json', 'r') as f:
    distros_dict = json2obj(f.read().replace('\n', ''))

print(distros_dict[0].refactorings[0].type)
