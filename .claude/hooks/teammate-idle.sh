#!/bin/bash
# TeammateIdle hook - keeps teammates productive
#
# When a teammate finishes its turn:
# - Exit 2 = prompt teammate to continue working
# - Exit 0 = no action needed, teammate can idle
#
# All teammates should message the team lead when idle
# to request more work via SendMessage.

# Prompt the teammate to message the team lead for work
echo "You are idle. Send REQUESTING_WORK to the team lead via SendMessage({ type: \"message\", recipient: \"team-lead\", content: \"REQUESTING_WORK\", summary: \"Requesting work\" }) and check your mailbox for pending messages."
exit 2
