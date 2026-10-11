#!/data/data/com.termux/files/usr/bin/bash

set -eu

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════╗"
echo "║     LOCATION TRACKER INSTALLER   ║"
echo "║       Developer: Firewall Crasher║"
echo "╚══════════════════════════════════╝"
echo -e "${RESET}"

if ! command -v pkg >/dev/null 2>&1; then
echo -e "${RED}[!] Termux is required.${RESET}"
exit 1
fi

echo -e "${YELLOW}[1/3] Updating packages...${RESET}"
pkg update -y

echo -e "${YELLOW}[2/3] Installing Python...${RESET}"
pkg install -y python

echo -e "${YELLOW}[3/3] Installing Flask...${RESET}"
python -m pip install flask

echo
if [ -f "Location Tracker.py" ]; then
echo -e "${GREEN}[✓] Installation complete!${RESET}"
echo -e "${CYAN}Run your application with:${RESET}"
echo 'python "Location Tracker.py"'
else
echo -e "${YELLOW}[!] Location Tracker.py not found.${RESET}"
echo "Place the main Python file in this directory."
fi