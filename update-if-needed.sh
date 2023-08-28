#!/bin/sh

# Fetch the newest code

cd /home/pi

git remote update
if ! $(git diff origin/main --quiet --exit-code)
then
    # Force pull
    git stash
    git reset --hard HEAD
    git pull
    # sudo reboot now
    echo "Updated successfully.";
else
    echo "Code is up-to-date."
fi
