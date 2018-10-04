import json


# class Refactoring:
#     def __init__(self, id, repository, sha1, author, time, refactorings):
#         self.id = id
#         self.repository = repository
#         self.sha1 = sha1
#         self.author = author
#         self.time = time
#         self.refactorings = refactorings


# with open('data/refactorings.json', 'r') as f:
#     distros_dict = json.loads(f.read().replace('\n', ''))
#     pythonObj = Refactoring(**distros_dict)
#     print(pythonObj)

from collections import namedtuple


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)


distros_dict = []

with open('data/refactorings.json', 'r') as f:
    distros_dict = json2obj(f.read().replace('\n', ''))

print(distros_dict[0].refactorings[0].type)

data = []

# use dict here
item = {
    "id": 1105075,
    "repository": "https://github.com/JetBrains/MPS.git",
    "sha1": "2bcd05a827ead109a56cb1f79a83dcd332f42888",
    "author": "Mihail Muhin",
    "time": "6/7/15 7:36 PM",
    "refactorings": [
            {
                "type": "Inline Method",
                "description": "<b>Inline Method</b> <code>public getLanguage(id SLanguageId, langName String, version int) : SLanguage</code> inlined to <code>public getLanguage(id SLanguageId, langName String) : SLanguage</code> in class <code>jetbrains.mps.smodel.adapter.structure.MetaAdapterFactory</code>"
            }
    ]
}
data.append(item)

with open('data/data.txt', 'w') as outfile:
    json.dump(data, outfile)

# class Test(object):
#     def __init__(self, data):
#         self.__dict__ = json.loads(data)


# test1 = Test(json_data)
# print(test1.a)


# loaded_json = json.loads(json_data)
# for x in loaded_json:
#     print("%s: %d" % (x, loaded_json[x]))
