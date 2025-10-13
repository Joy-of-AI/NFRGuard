#!/bin/bash
# Fix git history - Remove AWS credentials from all commits

echo "🔧 Fixing git history to remove AWS credentials..."

# Create a filter script
cat > /tmp/git-filter.sh << 'EOF'
#!/bin/bash
# Replace credentials in create_secure_env files

for file in src/agents/scripts/create_secure_env.sh src/agents/scripts/create_secure_env.ps1; do
    if [ -f "$file" ]; then
        sed -i 's/AWS_ACCESS_KEY_ID=AKIAXEVXYIFJ3N4NEE54/AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID_HERE/g' "$file"
        sed -i 's/AWS_SECRET_ACCESS_KEY=krMICTE6C1E\/FF2ns7xgDvUcTo53EeOp\/sv7Kikq/AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY_HERE/g' "$file"
        git add "$file" 2>/dev/null || true
    fi
done
EOF

chmod +x /tmp/git-filter.sh

# Run filter-branch to fix all commits
git filter-branch --force --tree-filter '/tmp/git-filter.sh' --prune-empty --tag-name-filter cat -- --all

# Clean up
echo "🧹 Cleaning up git references..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Git history fixed!"
echo ""
echo "Now run: git push origin main --force"

