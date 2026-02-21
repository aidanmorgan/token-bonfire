#!/bin/bash
# TeammateIdle hook - keeps workers productive
#
# When a teammate finishes its turn:
# - Exit 2 = prompt teammate to check for available work
# - Exit 0 = no action needed, teammate can idle
#
# This is project-agnostic: it only checks whether there
# are pending tasks remaining, not what the tasks contain.

# Prompt the teammate to check for work or review feedback
echo "Check your mailbox for review feedback or your next task."
exit 2
