

# RF-Radar: Wi-Fi Multipath Tomography & Presence Detection Report

## 1. Abstract

This report details the theoretical foundations and software implementation of RF-Radar, a passive Wi-Fi sensing tool designed to detect physical presence through radio frequency (RF) tomography. By analyzing the variance in the Received Signal Strength Indicator (RSSI) of 802.11 management frames, the system visualizes the electromagnetic "shadows" cast by physical bodies moving through a multipath propagation environment.

---

## 2. Physics Principles & Theoretical Framework

The core operation of this tool relies on wave propagation physics and the dielectric properties of the human body.

### 2.1 The Human Body as a Lossy Dielectric

In the 2.4 GHz and 5 GHz frequency bands used by standard Wi-Fi, the human body acts as a lossy dielectric medium (composed of ~60% water). When RF waves intersect a human body, they undergo:

* **Absorption:** A portion of the wave's kinetic energy is converted into heat.
* **Scattering/Diffraction:** Waves bend around the physical mass, altering the phase and amplitude of the transmitted signal.

### 2.2 Multipath Fading and Interference

In an indoor environment, signals rarely travel via a pure Line-of-Sight (LoS) path. The receiver antenna measures the superposition of the primary wave and multiple delayed, attenuated reflections (multipath).

The instantaneous received power $P_r$ can be modeled as the sum of $N$ multipath components:


$$P_r = \left| \sum_{i=1}^{N} a_i e^{j\phi_i} \right|^2$$


Where $a_i$ is the amplitude and $\phi_i$ is the phase of the $i$-th wave. When a person moves through the room, they alter specific $a_i$ and $\phi_i$ values, causing constructive or destructive interference. This manifests as a sudden drop or spike in the aggregate RSSI.

### 2.3 Motion Detection via Signal Variance

Instead of calculating absolute distance (which requires accurate path loss exponents), the system measures the relative variance from a rolling baseline. Motion is confirmed when:


$$\Delta \text{RSSI} = |\text{RSSI}_{\text{baseline}} - \text{RSSI}_{\text{current}}| \geq \text{Threshold}$$

---

## 3. System Architecture

The tool is built on a Python pipeline optimized for Linux environments, specifically leveraging raw socket access to bypass the OS networking stack.

### 3.1 Hardware Layer

* **Sensor Node:** A Wi-Fi interface (e.g., Realtek adapter) operating strictly in Monitor Mode.
* **Data Source:** 802.11 frames (specifically Beacons) intercepted via the physical layer, extracting the `RadioTap` header for instantaneous hardware-reported RSSI.

### 3.2 Software Pipeline

* **Ingestion:** The `scapy` library establishes a raw socket to capture frames asynchronously.
* **Filtering Engine:**
* **Ambient Mode:** Captures all 802.11 frames to map the aggregate noise floor.
* **Targeted Mode:** Applies a Berkeley Packet Filter (BPF) equivalent to isolate frames originating from a specific BSSID (`addr3`).


* **Data Structuring:** RSSI values are pushed into a fixed-size `numpy` buffer.
* **Visualization:** A background daemon thread handles the networking, while the main thread uses `matplotlib` (via the `Qt5Agg` backend) to render real-time UI updates at 10 Hz.

---

## 4. Visualization Modes

The system provides two distinct analytical paradigms:

* **1D Line Graph (Time-Series Variance):** Plots RSSI (dBm) over time. This is optimal for calibrating the system, establishing the noise floor, and observing the exact temporal duration of a diffraction event.
* **2D Heatmap (Spatial Density):** Transforms the 1D time-series data into a rolling matrix using a high-contrast colormap. Signal drops (shadows) are visualized as dark vertical streaks, allowing for intuitive pattern recognition of physical movement over a sustained period.

---

## 5. Experimental Methodology

To conduct a successful tomography scan using this architecture:

1. **Environment Calibration:** Lock the receiver to the target frequency channel to prevent channel hopping, ensuring a continuous sample rate.
2. **Baseline Establishment:** Run the script in an empty room to record the static multipath environment and determine the standard deviation of the ambient noise.
3. **Threshold Tuning:** Set the `-t` (threshold) parameter just above the static noise variance (typically 2.0 to 4.0 dBm).
4. **Execution:** Introduce physical movement. The system will alert dynamically when the $\Delta \text{RSSI}$ exceeds the defined threshold, confirming presence detection without active network authentication.

---

## 6. Conclusion

By exploiting the physical properties of RF wave propagation and the deterministic nature of 802.11 beacon intervals, RF-Radar provides a robust, passive mechanism for spatial awareness and tripwire implementation.
