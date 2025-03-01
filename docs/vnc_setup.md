# VNC Server Setup Documentation

This document outlines the VNC server setup on our system for remote desktop access.

## Installed Components
- TigerVNC Server
- noVNC (web-based VNC client)
- Firefox ESR browser
- XFCE desktop environment

## Configuration
- VNC Server running on port 5901
- noVNC web interface available on port 6080
- Using XFCE as the desktop environment

## How to Start/Restart the VNC Server
```bash
# Kill any existing VNC server
vncserver -kill :1

# Start a new VNC server
vncserver :1 -geometry 1280x800 -depth 24

# Restart the noVNC websockify service
sudo killall websockify && sudo websockify -D --web=/usr/share/novnc/ 6080 localhost:5901
```

## How to Connect
- Web browser: http://localhost:6080/vnc.html
- VNC client: connect to localhost:5901

## Notes
- The VNC server is configured using the ~/.vnc/xstartup script
- Firefox ESR is installed as the default browser
