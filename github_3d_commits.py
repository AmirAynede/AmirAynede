import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from github import Github, Auth
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
USERNAME = os.getenv('GITHUB_ACTOR')
TOKEN = os.getenv('GITHUB_TOKEN')
WEEKS_TO_SHOW = 26

def get_commit_data():
    auth = Auth.Token(TOKEN)
    g = Github(auth=auth)
    user = g.get_user(USERNAME)
    
    commit_matrix = np.zeros((7, WEEKS_TO_SHOW))
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(weeks=WEEKS_TO_SHOW)
    
    print(f"Fetching events for {USERNAME}...")
    
    events = user.get_events()
    count = 0
    
    for event in events:
        if event.type == "PushEvent":
            date = event.created_at
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            
            if date < start_date:
                continue
            
            delta = date - start_date
            week_idx = delta.days // 7
            day_idx = date.weekday()
            
            if 0 <= week_idx < WEEKS_TO_SHOW:
                # Handle Dict vs Object payload
                payload = event.payload
                commit_size = 0
                if isinstance(payload, dict):
                    commit_size = payload.get('size', 0)
                else:
                    commit_size = getattr(payload, 'size', 0)
                
                commit_matrix[day_idx][week_idx] += commit_size
                count += 1
    
    print(f"Found {count} push events in the last {WEEKS_TO_SHOW} weeks.")
    return commit_matrix

def create_cyber_graph(data):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    
    # Dark Background
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')
    
    # Make the "Glass Box" look (Transparent Panes)
    ax.xaxis.set_pane_color((0.1, 0.1, 0.1, 0.3))
    ax.yaxis.set_pane_color((0.1, 0.1, 0.1, 0.3))
    ax.zaxis.set_pane_color((0.1, 0.1, 0.1, 0.3))
    
    # Grid lines (Cyan but faint)
    ax.xaxis._axinfo["grid"]['color'] =  (0, 1, 1, 0.15)
    ax.yaxis._axinfo["grid"]['color'] =  (0, 1, 1, 0.15)
    ax.zaxis._axinfo["grid"]['color'] =  (0, 1, 1, 0.15)
    
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
    
    # --- LABELS (RESTORED) ---
    ax.set_title(f"3D COMMITS GRAPH: {USERNAME}", color='white', fontname='Courier New', pad=20)
    
    # Z-Axis (Commits)
    ax.set_zlabel('Commits', color='white', fontname='Courier New')
    ax.tick_params(axis='z', colors='white', labelsize=8)
    
    # Y-Axis (Days)
    ax.set_yticks([0, 2, 4, 6])
    ax.set_yticklabels(['Mon', 'Wed', 'Fri', 'Sun'], fontname='Courier New', fontsize=8, color='white')
    ax.tick_params(axis='y', colors='white')

    # X-Axis (Weeks)
    ax.set_xlabel('Weeks Ago', color='white', fontname='Courier New', labelpad=10)
    ax.tick_params(axis='x', colors='white', labelsize=8)
    
    # Note: I removed ax.axis('off') so these labels will now show up!

    return fig, ax

def update(angle, ax):
    ax.view_init(elev=25, azim=angle)
    return ax,

# --- EXECUTION ---
if __name__ == "__main__":
    try:
        data = get_commit_data()
        
        if data.sum() == 0:
            print("No recent push data found. Generating demo pattern...")
            data = np.random.randint(0, 5, (7, WEEKS_TO_SHOW))
        
        fig, ax = create_cyber_graph(data)
        
        print("Generating animation frames...")
        ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 360, 4), fargs=(ax,), interval=50)
        
        print("Saving GIF...")
        ani.save('cyber_graph.gif', writer='pillow', fps=20)
        print("SUCCESS: Saved to cyber_graph.gif")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        raise e
