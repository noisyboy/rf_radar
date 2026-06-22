---

# RF-Radar: Wi-Fi Tomography & Presence Detection

RF-Radar is a Python-based physical security and radio tomography tool. It leverages 802.11 management frame sniffing and RSSI (Received Signal Strength Indicator) variance to detect physical movement within a room.

By operating as a purely passive sensor, RF-Radar visualizes the "RF shadows" cast by humans or objects moving through a Wi-Fi multipath environment. Human bodies act as lossy dielectrics; as they intersect the line-of-sight or multipath reflections of ambient Wi-Fi signals, the tool detects and visualizes the resulting signal degradation in real-time.

## Features

* **Passive Sensing:** Operates entirely via monitor mode packet sniffing. No transmission or active connection to a network is required.
* **Dual Target Modes:**
* **Targeted Mode:** Locks onto a specific BSSID (router) to monitor a direct line-of-sight signal path.
* **Ambient Mode:** Monitors the aggregate RF noise floor of the entire room, capturing interference from all broadcasting devices.


* **Real-Time Visualization:** Renders data using a hardware-accelerated Matplotlib GUI. Choose between standard Line Graphs for fading analysis or 2D Heatmaps for spatial variance tracking.
* **Automated Motion Detection:** Utilizes a rolling baseline average to trigger visual and terminal alerts when a sudden dBm drop exceeds a user-defined threshold.
* **Terminal & GUI Integration:** Provides a high-contrast, hacker-themed interface designed for Linux desktop environments.

## Hardware Requirements

* A Linux-based operating system.
* A Wi-Fi network adapter that supports **Monitor Mode** and packet injection (e.g., Realtek RTL8188EUS, Atheros AR9271, or compatible MediaTek chipsets).

## Software Requirements

Ensure you have Python 3 installed. The tool requires root privileges (or specific network capabilities) to sniff raw packets.

Install the required Python dependencies:

```bash
pip install scapy numpy matplotlib PyQt5

```

*Note: `PyQt5` is required to ensure the Matplotlib GUI renders correctly in a separate thread on Linux desktop environments (like GNOME/Wayland).*

## Pre-Flight Setup

Before running the script, your wireless adapter must be placed into monitor mode.

```bash
# Bring the interface down
sudo ip link set wlan1 down

# Set to monitor mode
sudo iw dev wlan1 set type monitor

# Bring the interface up
sudo ip link set wlan1 up

```

*(Replace `wlan1` with your actual interface name found via `ip link show`)*

If you are targeting a specific router, ensure your adapter is tuned to the correct channel:

```bash
sudo iw dev wlan1 set channel 6

```

## Usage

RF-Radar is executed via the command line. Root access (via `sudo` or `setcap`) is required to capture packets.

### Command Line Arguments

* `-i`, `--interface` : **(Required)** The wireless interface in monitor mode.
* `-b`, `--bssid` : *(Optional)* The target MAC address of the router to track. If omitted, the tool defaults to Ambient Mode.
* `-v`, `--visual` : *(Optional)* The GUI mode. Choose between `line` (default) or `heat`.
* `-t`, `--threshold` : *(Optional)* The dBm drop required to trigger a motion alert. Default is `3.0`.

### Examples

**1. Ambient Heatmap (General Room Monitoring)**
Tracks all ambient RF signals in the room and visualizes the data as a heatmap. Useful for detecting general presence.

```bash
sudo python rf_radar.py -i wlan1 -v heat

```

**2. Targeted Line Graph (Precise Tripwire)**
Tracks a specific router to create a precise line-of-sight tripwire. Triggers an alert if the signal drops by more than 4.5 dBm.

```bash
sudo python rf_radar.py -i wlan1 -b AA:BB:CC:DD:EE:FF -v line -t 4.5

```

**3. Targeted Heatmap (Shadow Visualization)**
Visualizes the specific signal fading of a single router as a rolling matrix.

```bash
sudo python rf_radar.py -i wlan1 -b AA:BB:CC:DD:EE:FF -v heat

```

## Troubleshooting

* **No data appearing in the graph:** Ensure the adapter is on the same channel as the target BSSID. The script only captures packets on the currently tuned frequency.
* **Wayland/GUI Errors:** If the Matplotlib window crashes on launch, ensure you are running the script in an X11 environment or have the `QT_QPA_PLATFORM=xcb` environment variable set.
* **ValueError: Interface not found:** Double-check your interface name using `ip link show`. Adapters are often renamed dynamically when plugged into different USB ports.

## Disclaimer

This tool is designed for educational purposes, physics research, and authorized physical security auditing. Ensure you comply with all local laws and regulations regarding wireless network monitoring and packet capture in your jurisdiction.


<img width="1912" height="1079" alt="image" src="https://github.com/user-attachments/assets/3a77af01-46ce-495c-91d2-b640f8a03b4a" />

<img width="1906" height="1070" alt="image" src="https://github.com/user-attachments/assets/c83aadb3-4818-4131-a282-91505d51dbe9" />

