#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamp for log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/llmlens_${TIMESTAMP}.log"

# Start LLMLens with logging
pnpm start --characters="characters/llmlens.character.json" > "${LOG_FILE}" 2>&1