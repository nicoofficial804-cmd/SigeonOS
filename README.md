# SigeonOS — Keeping the sky smooth. 🕊️

SigeonOS is a high-performance, lightweight operating system featuring a sleek, interactive desktop shell built on top of a customized Arch Linux kernel. Combining the speed, security, and flexibility of Arch Linux with a custom-engineered PyQt6 user interface layer, SigeonOS offers a smooth, unified desktop environment with a modern, glassmorphic design language.

---

## 🚀 System Architecture & Kernel

Unlike standard desktop environments that run heavy display servers, SigeonOS runs directly on a customized Arch Linux kernel minimal boot stream:

- **Custom Arch Linux Kernel**: Highly optimized scheduler for low latency, customized drivers for instant peripheral recognition, and stripped-down services for ultra-fast boot times.
- **PyQt6 Desktop Shell**: Renders directly on a minimal window manager layer, bypassing standard heavy desktop suites (such as GNOME or KDE) to conserve system memory.
- **Arch TTY Terminal Integration**: Real terminal sessions link directly into `/bin/bash` with full ANSI escape sequence translation for colored output.
- **Secure Password Hashing**: User authentication database is protected using SHA-256 password hashing.
- **Automated Sandbox Handling**: Sandbox restrictions are automatically managed dynamically to allow Chromium-based applications (like Sigeon Browser) to run securely even under root permissions.

---

## 🎨 Design Language: Liquid Goon & Glassmorphism

SigeonOS is designed around visual fluidity and responsiveness:
- **Liquid Goon Backdrop**: Inspired by fluid physics, the desktop displays moving multi-colored aurora blobs that interact smoothly with screen-blend modes.
- **Interactive Stirring & Splash Ripples**: Moving windows or double-clicks generate fluid waves and splash animations.
- **True Glassmorphism**: Frosted acrylic paneling, linear light shines, drop shadows, and smooth micro-animations.

---

## 📦 Built-in Applications

SigeonOS comes pre-loaded with a suite of built-in system applications:

### 📂 File Explorer
A dual-mode file manager supporting the Sigeon Virtual Filesystem (VFS) and the underlying host disk. Features a shortcut sidebar, drag-and-drop file organization, right-click actions (New File, New Folder, Rename, Copy, Paste, Delete), and a system-wide Trash.

### 📝 Notes
A clean, minimalist text editor (replacing legacy "Feather Notes") optimized for text file management. Double-clicking any `.txt` file in File Explorer launches it instantly.

### 🎨 Paint
A rich graphics creation utility. Includes adjustable brush size settings, a system color picker, shape drawing (rectangles, ellipses), clear canvas controls, and native PNG/JPG export capabilities.

### 🎮 Flappy Pigeon
An arcade game calibrated with updated, highly-playable physics:
- Custom gravity coefficient (0.28) and terminal velocity dampening.
- Real-time sprite tilting based on flying path velocity.
- Dynamic scrolling ground stripe velocity and background parallax clouds.
- Progressive speed difficulty scaling.

### 📅 Calendar
A clean, clutter-free productivity planner. Renders monthly calendar grids, highlights the current date, and manages user meetings and schedule inputs. All legacy mockup data and AI placeholders have been removed.

### 💬 SigeonAI
A private AI chat assistant featuring an animated typing indicator, responsive layout styling, and clean chat bubbles.

### 💻 TTY Terminal
A terminal emulator providing direct execution channels to the Arch system shell. Features full ANSI escape code parsing to support colored CLI outputs.

### 🌐 Browser
A Chromium-powered web browser utilizing the `PyQt6-WebEngine` framework.

### 🌦️ Weather
A weather tracker showing live regional forecasts, humidity indices, wind velocities, and five-day forecast projections.

### ⚙️ Settings
A centralized panel managing system configurations:
- **Personalization**: Toggle dark mode, change wallpapers, and activate "Liquid Goon" theme parameters.
- **Network & Wi-Fi**: Perform real hardware interface network scans and establish secure connections.
- **Bluetooth**: Perform hardware peripheral scanning, pairing, and disconnection processes.
- **Accounts**: Manage system accounts, add new profiles, and change system passwords securely with hashed protection.

---

## 🔧 Installation & Running

Ensure you have Python 3.10+ and the required system packages installed:

```bash
# Install core system dependencies
pip install PyQt6 PyQt6-WebEngine psutil
```

Launch the SigeonOS desktop environment:

```bash
python main.py
```
