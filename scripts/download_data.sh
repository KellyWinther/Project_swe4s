#!/usr/bin/env bash
set -euo pipefail

# ======================================================
# Download data folder(s) from Google Drive using gdown

# Output directory for downloaded data
OUT_DIR="data"

# Google Drive folder URL (replace or add more as needed)
FOLDER_URL="https://drive.google.com/drive/folders/1MCQce7FXHNKEQg97zs5YrXFSZbxB_iDU?usp=drive_link"

echo "Creating output directory: ${OUT_DIR}"
mkdir -p "${OUT_DIR}"

# ------------------------------------------------------
# Check for gdown and install if needed
if ! command -v gdown >/dev/null 2>&1; then
    echo "gdown not found — installing it now..."
    pip install gdown
fi

# ------------------------------------------------------
# Download folder
echo "Downloading Google Drive folder:"
echo "  ${FOLDER_URL}"
echo "Saving to:"
echo "  ${OUT_DIR}"

gdown --folder "${FOLDER_URL}" -O "${OUT_DIR}"

echo "You have successfully downloaded the full and test data sets"
