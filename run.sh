#!/bin/bash
set -e

# Terminal 1 : Flask (root)
 /usr/bin/lxterminal \
  --title="Flask - app.py (root)" \
  --working-directory=/home/pi/buanderie-reservation-main \
  --command="bash -lc 'sudo -H /usr/bin/python3 /home/pi/buanderie-reservation-main/app.py; exec bash'" &

# Terminal 2 : UI menu (root ou pas selon besoin)
 /usr/bin/lxterminal \
  --title="Menu - menu.py (root)" \
  --working-directory=/home/pi \
  --command="bash -lc 'sudo -H /usr/bin/python3 /home/pi/menuV3.py; exec bash'" &
