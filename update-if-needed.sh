#!/bin/sh

# Fetch the newest code
# git fetch origin main

# Hard reset
## git reset --hard origin/master

changed=1
cd /home/pi

# git remote update && git status -uno | grep -q 'Your branch is behind' && changed=1
# git status -uno | grep -q 'Your branch is behind' && changed=1
git diff --quiet --exit-code && changed=0

if [ $changed = 1 ]; then
    # Force pull
    # git pull origin main --force
    git stash
    git reset --hard HEAD
    git pull
    # sudo reboot now
    echo "Updated successfully.";
else
    echo "Code is up-to-date."
fi
