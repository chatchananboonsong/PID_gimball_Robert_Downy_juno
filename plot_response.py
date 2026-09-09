import pandas as pd
import matplotlib.pyplot as plt

# โหลดข้อมูล
df = pd.read_csv("gimbal_response.csv")

# กรองเฉพาะจุดแรกของแต่ละจังหวะการยิง
df['fire_trigger'] = (df['is_fired'] == 1) & (df['is_fired'].shift(1, fill_value=0) == 0)
shot_events = df[df['fire_trigger']]

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

fig, (ax_yaw, ax_pitch) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, dpi=150)
fig.patch.set_facecolor('#ffffff')

# ----------------------------------------------------
# 1. แผง Yaw Angle
# ----------------------------------------------------
ax_yaw.plot(df['time_sec'], df['yaw_angle'], color='#1F77B4', linewidth=1.8, label='Yaw Angle (°)')
ax_yaw.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7, label='Center (0°)')
ax_yaw.set_ylabel('Yaw Angle (°)', fontsize=11, fontweight='bold')
ax_yaw.set_title('RoboMaster Gimbal Time Response (Yaw & Pitch Motion)', fontsize=13, fontweight='bold', pad=15)
ax_yaw.grid(True, linestyle=':', alpha=0.6)

# ----------------------------------------------------
# 2. แผง Pitch Angle
# ----------------------------------------------------
ax_pitch.plot(df['time_sec'], df['pitch_angle'], color='#2CA02C', linewidth=1.8, label='Pitch Angle (°)')
ax_pitch.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7, label='Center (0°)')
ax_pitch.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
ax_pitch.set_ylabel('Pitch Angle (°)', fontsize=11, fontweight='bold')
ax_pitch.grid(True, linestyle=':', alpha=0.6)

# ----------------------------------------------------
# 3. พล็อตจุดยิงและกล่องข้อความกำกับทั้ง Yaw และ Pitch
# ----------------------------------------------------
first_marker = True
for _, row in shot_events.iterrows():
    t_shot = row['time_sec']
    y_angle = row['yaw_angle']
    p_angle = row['pitch_angle']
    target_name = str(row['target']).replace(".0", "")
    
    lbl = 'IR Fired Point' if first_marker else ""
    first_marker = False

    # วาดจุดสีแดง ขอบดำ
    ax_yaw.scatter(t_shot, y_angle, color='#E74C3C', s=70, zorder=5, edgecolors='black', label=lbl)
    ax_pitch.scatter(t_shot, p_angle, color='#E74C3C', s=70, zorder=5, edgecolors='black', label=lbl)

    # --- กล่องข้อความบน Yaw ---
    offset_yaw = -24 if y_angle > 20 else 16
    ax_yaw.annotate(
        f"T{target_name} ({y_angle:.1f}°)",
        xy=(t_shot, y_angle),
        xytext=(0, offset_yaw),
        textcoords="offset points",
        ha='center',
        fontsize=7,
        fontweight='bold',
        color='#900C3F',
        bbox=dict(boxstyle='round,pad=0.12', facecolor='#FDEDEC', edgecolor='#E74C3C', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=0.8)
    )

    # --- กล่องข้อความบน Pitch ---
    # ถ้ามุม Pitch ต่ำกว่า -4 องศา ให้วางกล่องชี้ขึ้นด้านบนเพื่อไม่ให้ตกขอบล่าง
    offset_pitch = 16 if p_angle < -4 else -20
    ax_pitch.annotate(
        f"T{target_name} ({p_angle:.1f}°)",
        xy=(t_shot, p_angle),
        xytext=(0, offset_pitch),
        textcoords="offset points",
        ha='center',
        fontsize=7,
        fontweight='bold',
        color='#1E8449',
        bbox=dict(boxstyle='round,pad=0.12', facecolor='#EAFAF1', edgecolor='#27AE60', alpha=0.9),
        arrowprops=dict(arrowstyle='->', color='#27AE60', lw=0.8)
    )

# ขยายระยะแกน Y เพื่อไม่ให้กล่องข้อความชนขอบบน-ล่าง
y_min, y_max = ax_yaw.get_ylim()
ax_yaw.set_ylim(y_min - 8, y_max + 12)

p_min, p_max = ax_pitch.get_ylim()
ax_pitch.set_ylim(p_min - 1.5, p_max + 2.0)

ax_yaw.legend(loc='upper right', framealpha=0.9)
ax_pitch.legend(loc='upper right', framealpha=0.9)

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig("gimbal_yaw_pitch_compact.png", dpi=300)
print(">> บันทึกกราฟเรียบร้อย: gimbal_yaw_pitch_compact.png")
plt.show()