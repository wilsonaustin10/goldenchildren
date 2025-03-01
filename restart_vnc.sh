#!/bin/bash
# Kill any existing VNC server
vncserver -kill :1 2>/dev/null || echo "No VNC server running on display :1"

# Clean up lock files if they exist
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 2>/dev/null

# Start VNC server
vncserver :1 -geometry 1280x800 -depth 24

# Restart noVNC websockify service
sudo killall websockify 2>/dev/null
sudo websockify -D --web=/usr/share/novnc/ 6080 localhost:5901

echo "VNC server ready!"
echo "Connect via web browser: http://localhost:6080/vnc.html"
echo "Connect via VNC client: localhost:5901"
