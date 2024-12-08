#!/bin/bash

# Default log level (can be overridden by the LOG_LEVEL environment variable)
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FILE="run_steps.log" # Default log file location

# Log levels as an associative array (used for filtering log messages)
declare -A LOG_LEVELS
LOG_LEVELS[DEBUG]=0
LOG_LEVELS[INFO]=1
LOG_LEVELS[SUCCESS]=2
LOG_LEVELS[ERROR]=3

# Function to print logs with Docker-style formatting and colors
log() {
    local level="$1"
    local message="$2"
    local color=""

    # Map log level to colors
    case "$level" in
        DEBUG) color="\033[0;34m" ;;  # Blue
        INFO) color="\033[0;36m" ;;   # Cyan
        SUCCESS) color="\033[0;32m" ;;# Green
        ERROR) color="\033[0;31m" ;;  # Red
        *) color="\033[0m" ;;         # Reset
    esac

    # Build the log message
    local log_message="$(date '+%Y-%m-%d %H:%M:%S') [$level] $message"

    # Only log messages at or above the current log level
    if [ "${LOG_LEVELS[$level]}" -ge "${LOG_LEVELS[$LOG_LEVEL]}" ]; then
        # Print to console
        echo -e "${color}${log_message}\033[0m"
    fi

    # Always append to log file
    echo "$log_message" >> "$LOG_FILE"
}

# Function to execute steps
run_steps() {
    for step in "$@"; do
        log "INFO" "Starting step: $step"
        
        if declare -f "$step" > /dev/null; then
            if "$step"; then
                log "SUCCESS" "Step '$step' completed successfully!"
            else
                log "ERROR" "Step '$step' failed!"
                # Uncomment the next line to exit on failure
                # exit 1
            fi
        else
            log "ERROR" "Step '$step' is not defined!"
        fi

        log "INFO" "Finished step: $step"
        echo # Blank line for readability
    done
}

# Function to load external step definitions
load_steps() {
    local file="$1"
    if [[ -f "$file" ]]; then
        log "INFO" "Loading step definitions from $file..."
        source "$file"
        log "SUCCESS" "Step definitions loaded from $file."
    else
        log "ERROR" "Step definition file '$file' not found."
        exit 1
    fi
}

# Example functions
step_one() {
    log "DEBUG" "Executing Step One: preparing resources..."
    sleep 1 # Simulate work
    log "DEBUG" "Step One: resources prepared."
    return 0 # Success
}

step_two() {
    log "DEBUG" "Executing Step Two: performing critical operation..."
    sleep 1 # Simulate work
    log "DEBUG" "Step Two: critical operation encountered an issue."
    return 1 # Failure
}

step_three() {
    log "DEBUG" "Executing Step Three: cleaning up..."
    sleep 1 # Simulate work
    log "DEBUG" "Step Three: cleanup complete."
    return 0 # Success
}

# Main script execution
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    # Check for external step definition file
    if [[ -n "$1" ]]; then
        load_steps "$1"
        shift # Remove the step definition file argument
    fi

    # Run the remaining arguments as steps
    if [[ "$#" -gt 0 ]]; then
        run_steps "$@"
    else
        log "ERROR" "No steps provided to execute."
        exit 1
    fi
fi
