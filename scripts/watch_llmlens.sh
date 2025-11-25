#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

while true; do
    clear
    echo -e "${GREEN}=== LLMLens Activity Monitor ===${NC}"
    echo -e "${BLUE}Last updated: $(date)${NC}"
    echo "----------------------------------------"

    # Get most recent log file
    LATEST_LOG=$(ls -t logs | head -n1)
    if [ -n "$LATEST_LOG" ]; then
        echo -e "${YELLOW}Monitoring: $LATEST_LOG${NC}\n"
        python3 monitor.py "logs/$LATEST_LOG" | python3 -m json.tool
    else
        echo "No log files found in logs directory"
    fi

    # Wait 5 minutes before next check
    echo -e "\n${BLUE}Next update in 5 minutes...${NC}"
    sleep 300
done