import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from github import Github
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap

# --- CONFIGURATION ---
USERNAME = os.getenv('GITHUB_ACTOR') # Automatically gets your username
TOKEN = os.getenv('GITHUB_TOKEN')
WEEKS_TO_SHOW = 26  # Show last half-year (looks cleaner than full year)

def get_commit_data():
    """Fetches commit history and converts to a 7xWEEKS matrix."""
    g = Github(TOKEN)
    user = g.get_user(USERNAME)
    
    # Initialize matrix (7 days x WEEKS)
    commit_matrix = np.zeros((7, WEEKS_TO_SHOW))
    
    # Calculate start date
    today = datetime.now()
    start_date = today - timedelta(weeks=WEEKS_TO_SHOW)
    
    # Fetch events (this is a simplified way to get counts)
    # For perfect accuracy, you might need to iterate repos, but this is faster for visuals
    events = user.get_events()
    
    print(f"Fetching commits for {USERNAME}...")
    
    for event in events:
        if event.type == "PushEvent":
            date = event.created_at
            if date < start_date:
                continue
            
            # Calculate grid position
            delta = date - start_date
            week_idx = delta.days // 7
            day_idx = date.weekday() # 0=Mon, 6=Sun
            
            if 0 <= week_idx < WEEKS_TO_SHOW:
                commit_matrix[day_idx][week_idx] += event.payload.size

    return commit_matrix

def create_cyber_graph(data):
    # Setup the "Dark Mode" figure
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    
    # --- CYBER AESTHETICS ---
    fig.patch.set_facecolor('#050505') # Match your Scorpion background
    ax.set_facecolor('#050505')
    
    # Remove pane backgrounds for a "floating" look
    ax.xaxis.set_pane_color((0, 0, 0, 0))
    ax.yaxis.set_pane_color((0, 0, 0, 0))
    ax.zaxis.set_pane_color((0, 0, 0, 0))
    
    # Create the mesh
    _x = np.arange(WEEKS_TO_SHOW)
    _y = np.arange(7)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()
    
    # Flatten data for bars
    top = data.ravel()
    bottom = np.zeros_like(top)
    width = 0.8  # Bar thickness
    depth = 0.8
    
    # --- COLOR GRADIENT LOGIC ---
    # Create a custom colormap: Dark Blue -> Cyan -> White (Hot)
    colors = []
    max_height = max(top.max(), 1) # Avoid division by zero
    
    for height in top:
        intensity = height / max_height
        # Interpolate between simple colors based on height
        if intensity == 0:
            colors.append((0.1, 0.1, 0.1, 0.3)) # Ghostly grey for 0 commits
        else:
            # Neon Cyan/Green mix
            # R, G, B, Alpha
            colors.append((0.1, 0.5 + (0.5*intensity), 0.8 + (0.2*intensity), 0.9))

    # Plot the bars
    ax.bar3d(x, y, bottom, width, depth, top, shade=True, color=colors, edgecolor='none')
    
    # --- LABELS & TYPOGRAPHY ---
    ax.set_title(f"CONTRIBUTION SYSTEM: {USERNAME.upper()}", color='white', fontname='Courier New', pad=20)
    
    # Y-Axis: Days
    ax.set_yticks([0, 2, 4, 6])
    ax.set_yticklabels(['Mon', 'Wed', 'Fri', 'Sun'], fontname='Courier New', fontsize=8)
    
    # X-Axis: Remove clutter, just show "Timeline"
    ax.set_xlabel('Timeline (Weeks)', labelpad=10, fontname='Courier New', fontsize=8)
    ax.set_xticks([]) # Hide messy week numbers
    
    # Z-Axis
    ax.set_zlabel('Commits', fontname='Courier New', fontsize=8)
    
    # Hide the ugly grid lines
    ax.grid(False)
    
    # Add a floor grid manually for that "Tron" look
    ax.plot([0, WEEKS_TO_SHOW], [0, 0], [0, 0], color='#00ffcc', linewidth=0.5, alpha=0.5)
    ax.plot([0, 0], [0, 7], [0, 0], color='#00ffcc', linewidth=0.5, alpha=0.5)

    return fig, ax

def update(angle, ax):
    # Rotate the view
    ax.view_init(elev=25, azim=angle)
    return ax,

# --- EXECUTION ---
if __name__ == "__main__":
    try:
        data = get_commit_data()
        
        # If no data (e.g. new repo), fake some for the demo
        if data.sum() == 0:
            print("No recent data found. Generating demo pattern...")
            data = np.random.randint(0, 5, (7, WEEKS_TO_SHOW))
        
        fig, ax = create_cyber_graph(data)
        
        print("Generating animation...")
        # create a 360 degree rotation
        ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 360, 2), fargs=(ax,), interval=50)
        
        # Save
        ani.save('cyber_graph.gif', writer='pillow', fps=20)
        print("Done! Saved to cyber_graph.gif")
        
    except Exception as e:
        print(f"Error: {e}")
