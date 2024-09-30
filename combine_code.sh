#!/bin/bash

# Function to combine files
combine_files() {
    local source_dir=$1
    local output_file=$2
    shift 2
    local extensions=("$@")

    # Clear the output file if it exists
    > "$output_file"

    for ext in "${extensions[@]}"; do
        find "$source_dir" -type f -name "*.$ext" \
        ! -path "*/node_modules/*" \
        ! -name "*.lock" | while read -r file; do
            echo -e "\n\n# File: $file" >> "$output_file"
            cat "$file" >> "$output_file"
        done
    done
}

# Define directories and output files
frontend_dir="./frontend"
backend_dir="./backend"
frontend_output="combined_frontend.txt"
backend_output="combined_backend.txt"

# Define file extensions to include
frontend_extensions=("js" "jsx" "ts" "tsx" "css" "html")
backend_extensions=("py")

# Combine frontend files
combine_files "$frontend_dir" "$frontend_output" "${frontend_extensions[@]}"
echo "Frontend files combined into $frontend_output"

# Combine backend files
combine_files "$backend_dir" "$backend_output" "${backend_extensions[@]}"
echo "Backend files combined into $backend_output"