#!/bin/bash

# manage_path.sh
# Usage: ./manage_path.sh [add|remove] [directory] [--export]

ACTION=""
DIR=""
EXPORT_MODE=false

# Function to print usage
usage() {
    echo "Usage: $0 {add|remove} <directory> [--export]"
    echo "  add <dir>     : Add directory to PATH if not present"
    echo "  remove <dir>  : Remove directory from PATH"
    echo "  --export      : Output 'export PATH=...' command"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        add|remove)
            ACTION=$1
            shift
            ;;
        --export)
            EXPORT_MODE=true
            shift
            ;;
        *)
            if [[ -z "$DIR" ]]; then
                DIR=$1
                shift
            else
                echo "Unknown argument: $1"
                usage
            fi
            ;;
    esac
done

# Validate inputs
if [[ -z "$ACTION" || -z "$DIR" ]]; then
    usage
fi

# Get current PATH
CURRENT_PATH="$PATH"
NEW_PATH="$CURRENT_PATH"

# Normalize directory path (remove trailing slash)
DIR=${DIR%/}

if [[ "$ACTION" == "add" ]]; then
    # Check if directory is already in PATH
    if [[ ":$CURRENT_PATH:" == *":$DIR:"* ]]; then
        # Already exists, do nothing or just keep same
        NEW_PATH="$CURRENT_PATH"
    else
        # Prepend to PATH
        NEW_PATH="$DIR:$CURRENT_PATH"
    fi
elif [[ "$ACTION" == "remove" ]]; then
    # Remove directory from PATH
    # Replace :DIR: with :
    # Handle start and end cases
    
    # Logic: Split by :, filter, join
    NEW_PATH=$(echo "$CURRENT_PATH" | tr ':' '\n' | grep -vFx "$DIR" | paste -sd ':' -)
fi

# Output
if [[ "$EXPORT_MODE" == "true" ]]; then
    echo "export PATH=\"$NEW_PATH\""
else
    echo "New PATH would be:"
    echo "$NEW_PATH"
fi
