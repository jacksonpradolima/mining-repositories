import warnings

from travispy import TravisPy
# ignore travis package warnings
warnings.filterwarnings("ignore")

# First create a Travis instance using an Github access token
t = TravisPy.github_auth("b43b59e5a8d621516c3653b52b30f3df112a0f11")


repo = t.repo('DSpace/DSpace')

# https://travispy.readthedocs.io/en/latest/entities/#travispy.entities.Repo
print("Is it active?", repo.active)

# How to find?
build = t.build("DSpace/DSpace")

print(build)
