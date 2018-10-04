from github import Github

# Github instance using an access token
g = Github("b43b59e5a8d621516c3653b52b30f3df112a0f11")


def is_travis_project(slug):
    try:
        repo = g.get_repo(slug)
        content = repo.get_contents(".travis.yml")
        return True
    except Exception as e:
        return False


def get_slug_git_url(url):
    return url.replace("https://github.com/", "").replace(".git", "")
