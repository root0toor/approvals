#!/bin/bash
set +e  # Continue on errors

COLOR_BLUE="\033[0;94m"
COLOR_GREEN="\033[0;92m"
COLOR_RESET="\033[0m"

# Print useful output for user
echo -e "${COLOR_BLUE}
Welcome to your development container!%${COLOR_RESET}

This is how you can work with it:
- Files will be synchronized between your local machine and this container
- Some ports will be forwarded, so you can access this container via localhost
- Starting \`${COLOR_GREEN}sh start_scripts/start_app.sh${COLOR_RESET}\` to start the application
"

# Set terminal prompt
export PS1="\[${COLOR_BLUE}\]cloud-shell\[${COLOR_RESET}\] ./\W \[${COLOR_BLUE}\]\\$\[${COLOR_RESET}\] "
if [ -z "$BASH" ]; then export PS1="$ "; fi

# Include project's bin/ folder in PATH
export PATH="./bin:$PATH"

# Open shell
sh start_scripts/start_app.sh
