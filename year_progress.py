from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

# Ensure docs folder exists (for GitHub Pages publishing)
os.makedirs("docs", exist_ok=True)

# Get current date
current_date = datetime.now()

# Define year start and end
year_start = date(2025, 1, 1)
year_end = date(2025, 12, 31)

# Calculate total days in the year and days elapsed
total_days = (year_end - year_start).days + 1
days_elapsed = (current_date.date() - year_start).days

# Calculate percentage complete
percentage_complete = (days_elapsed / total_days) * 100

plt.style.use('default')
fig, ax = plt.subplots(figsize=(10, 2))
fig.patch.set_alpha(0.0)  # Transparent figure background
ax.set_facecolor('none')  # Transparent axes background

# Prettier gradient progress bar
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap

# Gradient colors (improved: blue → teal → yellow → pink)
cmap = LinearSegmentedColormap.from_list(
    "progress", ["#4f8cff", "#00e6c3", "#ffe066", "#ff6ec7"]
)
bar_width = days_elapsed / total_days

# Draw gradient bar
for i in np.linspace(0, bar_width, 100):
    ax.add_patch(Rectangle((i * total_days, -0.25), total_days / 100, 0.5,
                           color=cmap(i), linewidth=0))

# Draw remaining bar (faded, softer gray)
ax.add_patch(Rectangle((days_elapsed, -0.25), total_days - days_elapsed, 0.5,
                       color='#e3e6ee', alpha=0.22, linewidth=0))

# Red line for today (make it a bit more vivid)
ax.axvline(x=days_elapsed, color='#ff3b47', linestyle='--', alpha=0.85)

# Format axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_xlim(0, total_days)
ax.set_ylim(-0.5, 0.5)
ax.set_yticks([])
ax.set_title(
    f"2025: {percentage_complete:.2f}% | {days_elapsed}d elapsed | {total_days-days_elapsed}d left",
    color='#2a3a5e', fontweight='bold'
)

# Add annotations (improved colors)
ax.text(days_elapsed + 5, 0, f"Today: {current_date.strftime('%b %d')}",
        va='center', ha='left', color='#ff3b47', fontweight='bold')
ax.text(5, 0, "Start: Jan 01", va='center', ha='left', fontsize=8, color='#4f8cff')
ax.text(total_days - 5, 0, "End: Dec 31", va='center', ha='right', fontsize=8, color='#ff6ec7')

# Remove legend for cleaner look

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()

# Save into docs folder for GitHub Pages
fig.savefig("docs/progress.png", dpi=300, transparent=True)

# Save text version as well
with open("docs/progress.txt", "w") as f:
    f.write(f"2025 is {percentage_complete:.1f}% complete. {total_days - days_elapsed} days remaining.\n")
