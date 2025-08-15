from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

current_date = datetime.now()
year_start = date(2025, 1, 1)
year_end = date(2025, 12, 31)
total_days = (year_end - year_start).days + 1
days_elapsed = (current_date.date() - year_start).days
days_remaining = total_days - days_elapsed
percentage_complete = (days_elapsed / total_days) * 100

fig, ax = plt.subplots(figsize=(10, 2))
ax.barh(0, width=days_elapsed, height=0.5, color='#2ecc71')
ax.barh(0, width=total_days, height=0.5, color='#ecf0f1', alpha=0.3)

ax.axvline(x=days_elapsed, color='#e74c3c', linestyle='--', alpha=0.7)

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_xlim(0, total_days)
ax.set_ylim(-0.5, 0.5)
ax.set_yticks([])
ax.set_title(f"2025: {percentage_complete:.1f}% | {days_elapsed}d elapsed | {days_remaining}d left", fontweight='bold')

# Minimal annotation for today
ax.text(days_elapsed, 0.25, f"{current_date.strftime('%b %d')}", ha='center', va='bottom', color='#e74c3c', fontsize=8)

for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()
fig.savefig("progress.png", dpi=300)

with open("progress.txt", "w") as f:
    f.write(f"{percentage_complete:.1f}% complete, {days_remaining} days remaining.\n")
