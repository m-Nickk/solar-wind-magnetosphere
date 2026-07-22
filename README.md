# Solar Wind & Magnetosphere Simulation

A 2D/3D hybrid physics simulation built with Python and Pygame. It visualizes the interaction between the solar wind (charged particles emitted by the Sun) and Earth's compressed magnetic field (magnetosphere).

The simulation implements realistic physical concepts such as the **Boris integrator** for particle movement in a magnetic field, magnetic dipole compression, and Z-depth rendering sorting.

---

## Features
- **Physics-Based Simulation:** Uses a modified dipole formula to simulate magnetosphere compression on the sunward side and tail stretching on the night side.
- **Boris Algorithm:** Implements the mathematically stable Boris method for integrating charged particle trajectories in a magnetic field.
- **Dynamic Particle Trajectories:** Simulates positive and negative ions with distinct masses, charges, and colors (red/blue) with visual particle trails.
- **Pseudo-3D Rendering:** Sorts visual elements (Earth, field lines, particles) by their $Y$-axis depth for correct layer overlapping.

---

## Tech Stack
- **Language:** Python 3.x
- **Graphics & Windowing:** Pygame
- **Math & Vector Operations:** NumPy, Standard Math Library

---

## Getting Started

### Prerequisites
Make sure you have Python installed on your system. You will also need `pygame` and `numpy` libraries.

### Installation & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   ```

2. **Navigate to the project directory:**
   ```bash
   cd magnetosphere-simulation
   ```

3. **Install the required dependencies:**
   ```bash
   pip install pygame numpy
   ```

4. **Launch the simulation:**
   ```bash
   python main.py
   ```

---

## How It Works (Physics Overview)

### 1. Magnetic Field Approximation
The simulation models Earth's magnetic field as a distorted dipole. The field strength and shape change based on the position relative to the Sun:
- **Sunward side ($X < 0$):** The field is compressed by the incoming solar wind.
- **Tail side ($X > 0$):** The field lines are stretched out into a magnetotail.

### 2. Particle Dynamics
Particles are spawned near the Sun's surface and travel toward Earth. Each particle responds to the Lorentz force:
$$\mathbf{F} = q(\mathbf{v} \times \mathbf{B})$$

The simulation updates particle velocities using the **Boris method**, which preserves energy and phase-space volume perfectly for long-term orbital stability.
