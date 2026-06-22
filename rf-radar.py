import sys
import argparse
import threading
import numpy as np
import matplotlib
import matplotlib.colors as mcolors
# Force Qt5 backend for Arch Linux GUI compatibility
matplotlib.use('Qt5Agg') 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scapy.all import sniff, RadioTap, Dot11Beacon

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="RF Tomography & Wi-Fi Sensing Tool")
parser.add_argument("-i", "--interface", required=True, help="Wireless interface in monitor mode (e.g., wlan1)")
parser.add_argument("-b", "--bssid", required=False, default=None, help="Target BSSID to track (optional)")
parser.add_argument("-v", "--visual", choices=['line', 'heat'], default='line', help="Visualization mode: 'line' or 'heat'")
parser.add_argument("-t", "--threshold", type=float, default=3.0, help="Signal drop threshold for motion detection (dBm)")
args = parser.parse_args()

INTERFACE = args.interface
TARGET_BSSID = args.bssid.upper() if args.bssid else None
VISUAL_MODE = args.visual
MOTION_THRESHOLD = args.threshold

# --- DATA & STATE BUFFERS ---
BUFFER_SIZE = 100
rssi_values = [-90.0] * BUFFER_SIZE
motion_frames_left = 0  # Counter to keep the warning visible briefly

# ANSI Terminal Colors for Hacker Theme
T_GREEN = '\033[92m'
T_RED = '\033[91m'
T_RESET = '\033[0m'

def packet_callback(pkt):
    global motion_frames_left
    if pkt.haslayer(RadioTap):
        rssi = pkt[RadioTap].dBm_AntSignal
        if rssi is None:
            return

        process_packet = False
        
        # Filter Logic
        if TARGET_BSSID:
            if pkt.haslayer(Dot11Beacon) and pkt.haslayer('Dot11'):
                if pkt.addr3 and pkt.addr3.upper() == TARGET_BSSID:
                    process_packet = True
        else:
            process_packet = True

        if process_packet:
            # --- MOTION DETECTION LOGIC ---
            # Calculate the baseline from the last 10 packets (ignoring the very last one)
            baseline = np.mean(rssi_values[-10:-1])
            
            # Physics: A human body acts as a lossy dielectric, causing a sudden signal drop.
            if (baseline - rssi) >= MOTION_THRESHOLD:
                motion_frames_left = 10 # Keep the alert on screen for ~1 second
                status = f"{T_RED}[!!! MOTION DETECTED !!!] Drop: {abs(baseline-rssi):.1f} dBm{T_RESET}"
            else:
                status = f"{T_GREEN}[*] Scanning...{T_RESET}"

            # Update data buffers
            rssi_values.pop(0)
            rssi_values.append(rssi)
            
            # Terminal Output
            target_str = TARGET_BSSID if TARGET_BSSID else "AMBIENT WAVES"
            print(f"{T_GREEN}[{target_str}] RSSI: {rssi:0.1f} dBm | {status}          ", end='\r')

def start_sniffing():
    print(f"{T_GREEN}[SYSTEM] Initializing RF Matrix on {INTERFACE}...{T_RESET}")
    print(f"{T_GREEN}[SYSTEM] Motion Threshold set to {MOTION_THRESHOLD} dBm drop.{T_RESET}")
    try:
        sniff(iface=INTERFACE, prn=packet_callback, store=0)
    except Exception as e:
        print(f"\n{T_RED}[FATAL ERROR] Sniffing failed: {e}{T_RESET}")
        sys.exit(1)

# Start sniffer in a background thread
threading.Thread(target=start_sniffing, daemon=True).start()

# --- GUI SETUP (HACKER THEME) ---
# Custom colors
NEON_GREEN = '#00FF41'
DARK_GREEN = '#003B00'
BG_BLACK = '#050505'
ALERT_RED = '#FF003C'

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG_BLACK)
ax.set_facecolor(BG_BLACK)
ax.tick_params(colors=NEON_GREEN)
ax.spines['bottom'].set_color(NEON_GREEN)
ax.spines['left'].set_color(NEON_GREEN)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

title_str = f"TARGET: {TARGET_BSSID}" if TARGET_BSSID else "TARGET: AMBIENT NOISE FLOOR"
ax.set_title(title_str, color=NEON_GREEN, pad=15, fontweight='bold', fontfamily='monospace')
ax.set_xlabel("TIME (SAMPLES)", color=NEON_GREEN, fontfamily='monospace')

# Dynamic Warning Text Element
warning_text = ax.text(0.5, 0.90, '', transform=ax.transAxes, ha='center', 
                       va='center', color=ALERT_RED, fontsize=16, 
                       fontweight='bold', fontfamily='monospace')

# Initialize the chosen visualization
if VISUAL_MODE == 'heat':
    # Custom Black-to-Neon-Green Colormap
    hacker_cmap = mcolors.LinearSegmentedColormap.from_list("hacker", [BG_BLACK, DARK_GREEN, NEON_GREEN])
    heatmap_matrix = np.tile(rssi_values, (10, 1))
    img = ax.imshow(heatmap_matrix, aspect='auto', cmap=hacker_cmap, vmin=-90, vmax=-30)
    cbar = plt.colorbar(img)
    cbar.set_label('RSSI (dBm)', color=NEON_GREEN, fontfamily='monospace')
    cbar.ax.yaxis.set_tick_params(color=NEON_GREEN)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=NEON_GREEN, fontfamily='monospace')
    ax.set_ylabel("SPATIAL VARIANCE", color=NEON_GREEN, fontfamily='monospace')
    ax.get_yaxis().set_ticks([]) 
else:
    # Line Graph setup
    line, = ax.plot([], [], lw=2, color=NEON_GREEN)
    ax.set_ylim(-100, -20)
    ax.set_xlim(0, BUFFER_SIZE)
    ax.set_ylabel("RSSI (dBm)", color=NEON_GREEN, fontfamily='monospace')
    ax.grid(True, linestyle=':', color=DARK_GREEN, alpha=0.8)

def update(frame):
    global motion_frames_left
    
    # Handle the GUI Alert Flashing
    if motion_frames_left > 0:
        warning_text.set_text(">>> MOTION DETECTED <<<")
        # Flash the background slightly red
        ax.set_facecolor('#1a0000') 
        motion_frames_left -= 1
    else:
        warning_text.set_text("")
        ax.set_facecolor(BG_BLACK)

    if VISUAL_MODE == 'heat':
        img.set_data(np.tile(rssi_values, (10, 1)))
        return img, warning_text
    else:
        line.set_data(range(BUFFER_SIZE), rssi_values)
        return line, warning_text

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.tight_layout()
plt.show()
