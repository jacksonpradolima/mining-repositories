from travispy import TravisPy

import warnings
# ignore travis package warnings
warnings.filterwarnings("ignore")

# First create a Travis instance using an Github access token
t = TravisPy.github_auth("b43b59e5a8d621516c3653b52b30f3df112a0f11")


def is_active(repository):
    try:
        repo = t.repo(repository)
        return repo.active
    except:
        try:
            repo = t.repo(repository.lower())
            return repo.active
        except Exception as e:
            return False
    return status
