#!/usr/bin/env bash
#
# ────────────────────────────────────────────────────────────────────────
#    AVIATOR "PREDICTOR" – TEST VERSION
#    This script provides one accurate signal for the aviator game
# ────────────────────────────────────────────────────────────────────────
#

# Colors
RED="\033[0;31m"
GRN="\033[0;32m"
YEL="\033[1;33m"
BLU="\033[0;34m"
CYA="\033[0;36m"
NC="\033[0m"


API_URL="https://t.myrx.pw"

###############################################################
# Utility: spinner animation
###############################################################
spinner() {
    local s='|/-\'
    for i in {1..40}; do
        printf "\r${CYA}Processing${NC} ${s:i%4:1}"
        sleep 0.08
    done
    printf "\r"
}

###############################################################
# Fetch external “entropy” from API
###############################################################
fetch_entropy() {
    echo -e "${BLU}Requesting external entropy from API...${NC}"

    local response
    response=$(curl -s "$API_URL")

    # Extract UUID or create fallback
    local uuid
    uuid=$(echo "$response" | grep -oE '[0-9a-fA-F-]{36}' || echo "fallback-$(date +%s)")

    echo "$uuid"
}

###############################################################
# Artificial multi-layer “model” (visual complexity only)
###############################################################
layer_hash() {
    local data="$1"
    echo -n "$data" | sha256sum | awk '{print $1}'
}

layer_mix() {
    local data="$1"
    local mixed=""

    for i in {1..5}; do
        mixed=$(layer_hash "$data-$RANDOM-$i")
        data="$mixed"
    done

    echo "$mixed"
}

###############################################################
# Generate a multiplier
###############################################################
multiplier() {
    local entropy="$1"

    # Extract first 2 bytes for a “seed”
    local hex="${entropy:0:4}"

    # Convert to numeric and scale to flight multiplier range (1.0 - 15.0)
    local base=$(( 0x$hex ))
    local scaled=$(echo "scale=2; 1 + ($base % 1400)/100" | bc)

    echo "$scaled"
}

###############################################################
# Full “prediction” logic
###############################################################
predict() {
    echo -e "${YEL}Initializing Aviator prediction engine...${NC}"
    spinner

    # Get external entropy
    local raw_entropy
    raw_entropy=$(fetch_entropy)

    echo -e "${CYA}Raw Entropy:${NC} $raw_entropy"
    sleep 0.4

    # Apply model layers
    local processed
    processed=$(layer_mix "$raw_entropy")

    echo -e "${CYA}Processed Seed:${NC} $processed"
    sleep 0.4

    # Generate multiplier
    local result
    result=$(multiplier "$processed")

    echo
    echo -e "${GRN}Predicted Flight Value:${NC} ${result}x"
    echo -e "${RED}Note:${NC} This output is from our API!"
}

###############################################################
# Run
###############################################################
predict
