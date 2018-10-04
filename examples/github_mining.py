from github import Github

# First create a Github instance using an access token
g = Github("b43b59e5a8d621516c3653b52b30f3df112a0f11")

# Then play with your Github objects:
# for repo in g.get_user().get_repos():
#     print(repo.name)

repo = g.get_repo("DSpace/DSpace")
print("Repository Name: ", repo.name)

# Get repository topics
print("\nRepository Topics:")
print(repo.get_topics())

# Get Pull Request by Number
print("\nRepository Specific Pull Request:")
print(repo.get_pull(664))

# Get Pull Requests by Query
# print("\nRepository Pull Requests:")
# pulls = repo.get_pulls(state='open', sort='created', base='master')
# for pr in pulls:
#     print(pr.number)

# a = repo.get_commits()
# for i in a:
#     print(i)

# ATTENTION: Get the url and observe the object API
# print(repo.get_commit(sha="d51c39134e4caad5d5abaf84a497599c063668c5").url)

print(repo.get_commit(sha="d51c39134e4caad5d5abaf84a497599c063668c5").commit.message)
