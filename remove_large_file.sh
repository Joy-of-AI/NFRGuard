#!/bin/bash
# Script to remove eksctl.exe from git history

echo "Removing eksctl.exe from git history..."

# Remove the file from all commits
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch src/agents/eksctl/eksctl.exe' \
  --prune-empty --tag-name-filter cat -- --all

echo "Cleaning up..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Done! Now you can push:"
echo "git push origin main --force"

