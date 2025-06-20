#!/bin/bash
# Improved GitHub Repository Setup Commands with proper error handling
# Repository URL: https://github.com/itsocialist/mcp-universal-framework

set -e  # Exit on any error

echo "🚀 Setting up GitHub repository with proper validation..."

# Navigate to project directory
cd /Users/briandawson/Development/mcp-universal-framework

# Verify we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in the correct project directory"
    exit 1
fi

echo "📁 Current directory validated"

# Remove any existing origin remote (in case of previous attempts)
git remote remove origin 2>/dev/null || true

# Add the correct GitHub remote
echo "🔗 Adding GitHub remote..."
git remote add origin https://github.com/itsocialist/mcp-universal-framework.git

# Verify remote was added
if ! git remote -v | grep -q "itsocialist/mcp-universal-framework"; then
    echo "❌ Error: Failed to add remote repository"
    exit 1
fi

echo "✅ Remote repository added successfully"

# Set main branch
git branch -M main

# Verify we have commits to push
if [ -z "$(git log --oneline 2>/dev/null)" ]; then
    echo "❌ Error: No commits found to push"
    exit 1
fi

echo "📝 Commits verified"

# Push code to GitHub with error checking
echo "⬆️ Pushing code to GitHub..."
if git push -u origin main; then
    echo "✅ Code pushed successfully"
else
    echo "❌ Error: Failed to push code to GitHub"
    exit 1
fi

# Push the release tag with error checking
echo "🏷️ Pushing release tag..."
if git push origin v1.0.0; then
    echo "✅ Tag v1.0.0 pushed successfully"
else
    echo "❌ Error: Failed to push tag v1.0.0"
    exit 1
fi

# Final verification
echo "🔍 Verifying repository setup..."
git remote -v
echo ""
git log --oneline -3
echo ""
git tag

echo ""
echo "🎉 Repository successfully pushed to GitHub!"
echo "🔗 Repository URL: https://github.com/itsocialist/mcp-universal-framework"
echo ""
echo "📋 Next steps:"
echo "   1. Go to https://github.com/itsocialist/mcp-universal-framework"
echo "   2. Verify all files are present (should see 32+ files)"
echo "   3. Create a release from tag v1.0.0:"
echo "      - Go to https://github.com/itsocialist/mcp-universal-framework/releases"
echo "      - Click 'Create a new release'"
echo "      - Choose tag v1.0.0"
echo "      - Title: 'MCP Universal Framework v1.0.0'"
echo "      - Copy description from CHANGELOG.md"
echo "      - Mark as 'Latest release'"
echo "   4. Test the repository is accessible"
echo ""
echo "✅ Phase 3: GitHub Upload - COMPLETE!"
