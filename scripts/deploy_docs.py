#!/usr/bin/env python3
"""
Script to deploy documentation to GitHub Pages.

This script builds the documentation and pushes it to the gh-pages branch.
Normally this is handled automatically by GitHub Actions, but this script
can be used for manual deployment if needed.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    """Deploy documentation to GitHub Pages."""
    # Get the repository root
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / "docs"
    build_dir = docs_dir / "_build" / "html"
    
    print("🏗️  Building documentation...")
    
    # Change to docs directory
    os.chdir(docs_dir)
    
    # Clean previous build
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build documentation
    run_command("sphinx-build -b html . _build/html")
    
    print("✅ Documentation built successfully!")
    
    # Check if we're in a git repository
    os.chdir(repo_root)
    try:
        run_command("git status")
    except:
        print("❌ Not in a git repository. Cannot deploy to GitHub Pages.")
        sys.exit(1)
    
    # Check if gh-pages branch exists
    try:
        run_command("git show-ref --verify --quiet refs/heads/gh-pages")
        branch_exists = True
    except:
        branch_exists = False
    
    print("📤 Deploying to GitHub Pages...")
    
    # Create or switch to gh-pages branch
    if not branch_exists:
        print("Creating gh-pages branch...")
        run_command("git checkout --orphan gh-pages")
        run_command("git rm -rf .")
    else:
        print("Switching to gh-pages branch...")
        run_command("git checkout gh-pages")
        run_command("git rm -rf .")
    
    # Copy built documentation
    for item in build_dir.iterdir():
        if item.is_dir():
            shutil.copytree(item, repo_root / item.name)
        else:
            shutil.copy2(item, repo_root / item.name)
    
    # Create .nojekyll file to disable Jekyll processing
    (repo_root / ".nojekyll").touch()
    
    # Add and commit files
    run_command("git add .")
    run_command('git commit -m "Deploy documentation"')
    
    # Push to GitHub
    print("🚀 Pushing to GitHub...")
    run_command("git push origin gh-pages")
    
    # Switch back to main branch
    run_command("git checkout main")
    
    print("✅ Documentation deployed successfully!")
    print("📖 Your documentation will be available at:")
    print("   https://your-username.github.io/AlviaOrange/")
    print("")
    print("Note: It may take a few minutes for GitHub Pages to update.")

if __name__ == "__main__":
    main() 