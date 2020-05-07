import warnings

from travispy import TravisPy
# ignore travis package warnings
warnings.filterwarnings("ignore")

# First create a Travis instance using an Github access token
t = TravisPy.github_auth("b43b59e5a8d621516c3653b52b30f3df112a0f11")


repo = t.repo('DSpace/DSpace')

# https://travispy.readthedocs.io/en/latest/entities/#travispy.entities.Repo
print("Is it active?", repo.active)

# print([p.pull_request_number for p in TravisPy().builds(
#     slug='DSpace/DSpace', event_type='pull_request')])

builds = TravisPy().builds(slug='DSpace/DSpace')

#print([p.pull_request_number for p in builds])
# print(builds[0])
print(t.build(6012))
