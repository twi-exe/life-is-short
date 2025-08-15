from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

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

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 2))

# Create progress bar
ax.barh(0, width=days_elapsed, height=0.5, color='#2ecc71', label=f'Completed: {percentage_complete:.1f}%')
ax.barh(0, width=total_days, height=0.5, color='#ecf0f1', alpha=0.3, label='Remaining')

# Add vertical line for today
ax.axvline(x=days_elapsed, color='#e74c3c', linestyle='--', alpha=0.7)

# Format axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_xlim(0, total_days)
ax.set_ylim(-0.5, 0.5)
ax.set_yticks([])
ax.set_title(f"2025 Progress: {percentage_complete:.1f}% Complete", fontweight='bold')

# Add annotations
ax.text(days_elapsed + 5, 0, f"Today: {current_date.strftime('%b %d')}", 
        va='center', ha='left', color='#e74c3c', fontweight='bold')
ax.text(5, 0, "Start: Jan 01", va='center', ha='left', fontsize=8)
ax.text(total_days - 5, 0, "End: Dec 31", va='center', ha='right', fontsize=8)

# Legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()

# Save image (GitHub Pages will serve this)
fig.savefig("progress.png", dpi=300)

# Also save text version
with open("progress.txt", "w") as f:
    f.write(f"2025 is {percentage_complete:.1f}% complete. {total_days - days_elapsed} days remaining.\n")
