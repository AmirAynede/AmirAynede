import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from github import Github
from datetime import datetime, timedelta

# --- CONFIGURATION ---
USERNAME = os.getenv('GITHUB_ACTOR')
TOKEN = os.getenv('GITHUB_TOKEN')
WEEKS_TO_SHOW = 26

def get_commit_data():
    g = Github(TOKEN)
    user = g.get_user(USERNAME)
    commit_matrix = np.zeros((7, WEEKS_TO_SHOW))
    today = datetime.now()
    start_date = today - timedelta(weeks=WEEKS_TO_SHOW)
    
    # Simple console log to prove it's running
    print(f"Fetching events for {USERNAME}...")
    
    events = user.get_events()
    count = 0
    
    for event in events:
        if event.type == "PushEvent":
            date = event.created_at
            if date < start_date:
                continue
            delta = date - start_date
            week_idx = delta.days // 7
            day_idx = date.weekday()
            if 0 <= week_idx < WEEKS_TO_SHOW:
                commit_matrix[day_idx][week_idx] += event.payload.size
                count += 1
    
    print(f"Found {count} push events in the last {WEEKS_TO_SHOW} weeks.")
    return commit_matrix

def create_cyber_graph(data):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')
    ax.xaxis.set_pane_color((0, 0, 0, 0))
    ax.yaxis.set_pane_color((0, 0, 0, 0))
    ax.zaxis.set_pane_color((0, 0, 0, 0))
    
    _x = np.arange(WEEKS_TO_SHOW)
    _y = np.arange(7)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()
    top = data.ravel()
    bottom = np.zeros_like(top)
    width = 0.8
    depth = 0.8
    
    colors = []
    max_height = max(top.max(), 1)
    for height in top:
        intensity = height / max_height
        if intensity == 0:
            colors.append((0.1, 0.1, 0.1, 0.3))
        else:
            colors.append((0.1, 0.5 + (0.5*intensity), 0.8 + (0.2*intensity), 0.9))

    ax.bar3d(x, y, bottom, width, depth, top, shade=True, color=colors, edgecolor='none')
    ax.set_title(f"CONTRIBUTION SYSTEM: {USERNAME}", color='white', fontname='Courier New', pad=20)
    ax.axis('off') # Cleaner look
    return fig, ax

def update(angle, ax):
    ax.view_init(elev=25, azim=angle)
    return ax,

# --- EXECUTION ---
if __name__ == "__main__":
    # REMOVED TRY/EXCEPT BLOCK TO EXPOSE ERRORS
    data = get_commit_data()
    
    if data.sum() == 0:
        print("No data found. Generating demo pattern...")
        data = np.random.randint(0, 5, (7, WEEKS_TO_SHOW))
    
    fig, ax = create_cyber_graph(data)
    
    print("Generating animation frames...")
    ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 360, 4), fargs=(ax,), interval=50)
    
    print("Saving GIF...")
    ani.save('cyber_graph.gif', writer='pillow', fps=20)
    print("SUCCESS: Saved to cyber_graph.gif")
