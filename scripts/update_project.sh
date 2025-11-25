#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CUSTOM_DIR="/home/mike/llmlens-custom"
PROJECT_DIR="/home/mike/eliza"

echo -e "${YELLOW}Backing up current custom files...${NC}"
# Backup current custom files
cp -rv "$PROJECT_DIR/characters/llmlens."* "$CUSTOM_DIR/characters/"
cp -v "$PROJECT_DIR/.env" "$CUSTOM_DIR/config/"
cp -v "$PROJECT_DIR/monitor.py" "$PROJECT_DIR/generate_poster.py" "$PROJECT_DIR/"*.sh "$CUSTOM_DIR/scripts/"

echo -e "${YELLOW}Updating main project...${NC}"
# Update main project
cd "$PROJECT_DIR"
git stash
git pull origin main || git pull origin master

echo -e "${YELLOW}Restoring custom files...${NC}"
# Restore custom files
cp -rv "$CUSTOM_DIR/characters/"* "$PROJECT_DIR/characters/"
cp -v "$CUSTOM_DIR/config/.env" "$PROJECT_DIR/"
cp -v "$CUSTOM_DIR/scripts/"* "$PROJECT_DIR/"

echo -e "${GREEN}Update complete!${NC}"
echo "You may need to restart the agent for changes to take effect."