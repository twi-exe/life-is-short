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

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 2))
fig.patch.set_facecolor('#181818')
ax.set_facecolor('#181818')

# White progress bar
ax.barh(0, width=days_elapsed, height=0.5, color='white', label=f'{percentage_complete:.1f}%')
ax.barh(0, width=total_days, height=0.5, color='#444', alpha=0.3, label='Remaining')

# Red line for today
ax.axvline(x=days_elapsed, color='#ff5555', linestyle='--', alpha=0.8)

# Format axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_xlim(0, total_days)
ax.set_ylim(-0.5, 0.5)
ax.set_yticks([])
ax.set_title(f"2025: {percentage_complete:.1f}% | {days_elapsed}d elapsed | {total_days-days_elapsed}d left", color='white', fontweight='bold')

# Add annotations
ax.text(days_elapsed + 5, 0, f"Today: {current_date.strftime('%b %d')}", 
        va='center', ha='left', color='#ff5555', fontweight='bold')
ax.text(5, 0, "Start: Jan 01", va='center', ha='left', fontsize=8, color='white')
ax.text(total_days - 5, 0, "End: Dec 31", va='center', ha='right', fontsize=8, color='white')

# Legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()

# Save into docs folder for GitHub Pages
fig.savefig("docs/progress.png", dpi=300)

# Save text version as well
with open("docs/progress.txt", "w") as f:
    f.write(f"2025 is {percentage_complete:.1f}% complete. {total_days - days_elapsed} days remaining.\n")
