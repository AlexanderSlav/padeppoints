#!/usr/bin/env python3
"""
Visualize Alembic migration hierarchy by parsing revision files.
Shows the dependency tree of migrations based on revision and down_revision fields.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def parse_migration_file(filepath: Path) -> Tuple[Optional[str], Optional[str], str]:
    """
    Parse a migration file to extract revision, down_revision, and description.
    
    Returns: (revision, down_revision, description)
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Handle both with and without type annotations
    revision_match = re.search(r"revision(?:\s*:\s*str)?\s*=\s*['\"]([^'\"]+)['\"]", content)
    down_revision_match = re.search(r"down_revision(?:\s*:\s*Union\[str,\s*None\])?\s*=\s*['\"]([^'\"]+)['\"]", content)
    
    revision = revision_match.group(1) if revision_match else None
    down_revision = down_revision_match.group(1) if down_revision_match else None
    
    # Handle None values for down_revision (initial migration)
    if not down_revision_match:
        down_revision_none = re.search(r"down_revision(?:\s*:\s*Union\[str,\s*None\])?\s*=\s*None", content)
        if down_revision_none:
            down_revision = None
    
    # Extract description from filename
    filename = filepath.stem
    parts = filename.split('_', 1)
    description = parts[1] if len(parts) > 1 else filename
    
    return revision, down_revision, description


def build_migration_tree(versions_dir: Path) -> Dict[Optional[str], List[Tuple[str, str]]]:
    """
    Build a tree structure of migrations.
    
    Returns: Dictionary mapping parent revision to list of (child_revision, description) tuples
    """
    tree = {}
    revisions = {}
    
    # Parse all migration files
    for filepath in versions_dir.glob("*.py"):
        if filepath.stem == "__pycache__":
            continue
            
        revision, down_revision, description = parse_migration_file(filepath)
        if revision:
            revisions[revision] = (down_revision, description)
    
    # Build tree structure
    for revision, (down_revision, description) in revisions.items():
        if down_revision not in tree:
            tree[down_revision] = []
        tree[down_revision].append((revision, description))
    
    return tree, revisions


def find_heads(tree: Dict, revisions: Dict) -> List[str]:
    """Find all head revisions (revisions with no children)."""
    all_revisions = set(revisions.keys())
    parent_revisions = set()
    
    for children in tree.values():
        for child, _ in children:
            if child in revisions:
                parent_revision = revisions[child][0]
                if parent_revision:
                    parent_revisions.add(parent_revision)
    
    heads = all_revisions - parent_revisions
    return list(heads)


def print_tree(tree: Dict, revisions: Dict, revision: Optional[str] = None, 
               indent: int = 0, printed: Set[str] = None, is_last: bool = True,
               prefix: str = ""):
    """
    Recursively print the migration tree.
    """
    if printed is None:
        printed = set()
    
    if revision in tree:
        children = sorted(tree[revision], key=lambda x: x[0])
        for i, (child_rev, description) in enumerate(children):
            if child_rev in printed:
                continue
            printed.add(child_rev)
            
            is_last_child = (i == len(children) - 1)
            
            # Determine the connector
            if indent == 0:
                connector = ""
                new_prefix = ""
            else:
                connector = "└── " if is_last_child else "├── "
                new_prefix = prefix + ("    " if is_last_child else "│   ")
            
            # Check if this is a head revision
            is_head = child_rev not in tree or len(tree[child_rev]) == 0
            head_marker = " [HEAD]" if is_head else ""
            
            # Print the revision
            print(f"{prefix}{connector}{child_rev[:12]} - {description}{head_marker}")
            
            # Recursively print children
            print_tree(tree, revisions, child_rev, indent + 1, printed, 
                      is_last_child, new_prefix)


def visualize_branches(tree: Dict, revisions: Dict):
    """
    Visualize migrations showing any branches or merges.
    """
    # Find all branch points (revisions with multiple children)
    branch_points = {}
    for parent, children in tree.items():
        if len(children) > 1:
            branch_points[parent] = children
    
    if branch_points:
        print("\n" + "="*60)
        print("BRANCH POINTS DETECTED:")
        print("="*60)
        for parent, children in branch_points.items():
            parent_desc = revisions[parent][1] if parent and parent in revisions else "Initial"
            print(f"\nFrom: {parent[:12] if parent else 'None'} ({parent_desc})")
            print("Branches into:")
            for child_rev, desc in children:
                print(f"  → {child_rev[:12]} - {desc}")


def main():
    # Find the alembic versions directory
    current_dir = Path.cwd()
    versions_dir = current_dir / "alembic" / "versions"
    
    if not versions_dir.exists():
        print("Error: alembic/versions directory not found!")
        print(f"Looking in: {versions_dir}")
        return
    
    print("="*60)
    print("ALEMBIC MIGRATION HIERARCHY")
    print("="*60)
    
    tree, revisions = build_migration_tree(versions_dir)
    
    if not revisions:
        print("No migration files found!")
        return
    
    # Print statistics
    print(f"\nTotal migrations: {len(revisions)}")
    heads = find_heads(tree, revisions)
    print(f"Head revision(s): {len(heads)}")
    if heads:
        for head in heads:
            print(f"  - {head[:12]} ({revisions[head][1]})")
    
    print("\n" + "="*60)
    print("MIGRATION TREE:")
    print("="*60 + "\n")
    
    # Start from None (root) to show all migrations
    if None in tree:
        print("[Initial Migration]")
        print_tree(tree, revisions, None)
    else:
        # If there's no None root, find the actual root(s)
        all_down_revisions = set(rev[0] for rev in revisions.values() if rev[0])
        roots = set(revisions.keys()) - all_down_revisions
        
        for root in roots:
            print(f"{root[:12]} - {revisions[root][1]} [ROOT]")
            print_tree(tree, revisions, root)
    
    # Check for branches
    visualize_branches(tree, revisions)
    
    # Check for potential issues
    print("\n" + "="*60)
    print("ANALYSIS:")
    print("="*60)
    
    # Check for orphaned migrations
    all_parents = set()
    for rev, (down_rev, _) in revisions.items():
        if down_rev:
            all_parents.add(down_rev)
    
    orphaned = all_parents - set(revisions.keys()) - {None}
    if orphaned:
        print("\n⚠️  WARNING: References to non-existent revisions:")
        for orph in orphaned:
            print(f"  - {orph}")
    
    # Check for multiple heads
    if len(heads) > 1:
        print("\n⚠️  WARNING: Multiple heads detected!")
        print("This might indicate parallel branches that need to be merged.")
    
    if not orphaned and len(heads) == 1:
        print("\n✅ Migration hierarchy looks healthy!")


if __name__ == "__main__":
    main()