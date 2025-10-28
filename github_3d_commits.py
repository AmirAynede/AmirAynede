from github import Github
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import os

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_ACTOR")

g = Github(token)
user = g.get_user(username)

dates = []
for repo in user.get_repos():
    try:
        commits = repo.get_commits(author=user)
        for commit in commits:
            dates.append(commit.commit.author.date.date())
    except:
        continue

counter = Counter(dates)
if not counter:
    print("No commits found.")
    exit()

start = min(counter.keys())
end = max(counter.keys())
all_days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
values = [counter.get(day, 0) for day in all_days]

weeks = len(all_days) // 7
Z = np.array(values[:weeks * 7]).reshape(weeks, 7)

plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 5))
ax = fig.add_subplot(111, projection='3d')

_x = np.arange(Z.shape[0])
_y = np.arange(Z.shape[1])
_xx, _yy = np.meshgrid(_x, _y)
x, y = _xx.ravel(), _yy.ravel()
top = Z.T.ravel()
bottom = np.zeros_like(top)
width = depth = 0.8

ax.bar3d(x, y, bottom, width, depth, top, shade=True, color='#6ee7b7')
ax.set_xlabel('Weeks')
ax.set_ylabel('Days')
ax.set_zlabel('Commits')
ax.set_title(f'{username} GitHub Commits (3D)', pad=20)

plt.tight_layout()
plt.savefig("3d_commits.png", dpi=150)
