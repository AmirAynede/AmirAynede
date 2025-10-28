from github import Github
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from collections import Counter
import os
from matplotlib import animation
import time

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_ACTOR")

print(f"🔍 Fetching commits for user: {username}")

g = Github(token)
user = g.get_user(username)

# --- Gather commit dates ---
dates = []
for repo in user.get_repos():
    try:
        commits = repo.get_commits(author=user)
        for commit in commits:
            dates.append(commit.commit.author.date.date())
    except Exception as e:
        print(f"⚠️ Skipped repo {repo.name}: {e}")
        continue

if not dates:
    print("❌ No commits found — aborting GIF generation.")
    exit()

print(f"✅ Found {len(dates)} total commits.")

# --- Process commit data ---
from datetime import timedelta
from collections import Counter

counter = Counter(dates)
start = min(counter.keys())
end = max(counter.keys())
all_days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
values = [counter.get(day, 0) for day in all_days]

weeks = len(all_days) // 7
Z = np.array(values[:weeks * 7]).reshape(weeks, 7)

# --- Plot setup ---
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

# --- Animation ---
def rotate(angle):
    ax.view_init(elev=30, azim=angle)

anim = animation.FuncAnimation(fig, rotate, frames=np.arange(0, 360, 3), interval=100)

# --- Save explicitly to repo root ---
output_path = os.path.join(os.getcwd(), "3d_commits.gif")
print(f"💾 Saving to: {output_path}")

anim.save(output_path, writer="pillow", fps=20)
time.sleep(2)

# --- Verify file ---
if os.path.exists(output_path):
    size_kb = os.path.getsize(output_path) / 1024
    print(f"🎥 GIF generated successfully! Size: {size_kb:.2f} KB")
else:
    print("❌ GIF file not found after saving!")

# --- Show directory contents ---
print("\n📂 Files in current directory:")
for f in os.listdir(os.getcwd()):
    print(" -", f)

plt.close(fig)
