"""Git operations tools for version control."""
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from git import Repo, InvalidGitRepositoryError, GitCommandError


class GitOperations:
    """Tools for Git version control operations."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self._repo = None

    @property
    def repo(self) -> Repo:
        """Get or initialize Git repository."""
        if self._repo is None:
            try:
                self._repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                raise ValueError(f"Not a git repository: {self.repo_path}")
        return self._repo

    async def git_status(self) -> Dict[str, any]:
        """
        Get current repository status.

        Returns:
            Dictionary with repository status information
        """
        try:
            repo = self.repo

            # Get current branch
            current_branch = repo.active_branch.name if not repo.head.is_detached else "HEAD detached"

            # Get modified files
            modified_files = [item.a_path for item in repo.index.diff(None)]

            # Get staged files
            staged_files = [item.a_path for item in repo.index.diff("HEAD")]

            # Get untracked files
            untracked_files = repo.untracked_files

            # Check if ahead/behind remote
            tracking_branch = repo.active_branch.tracking_branch()
            ahead_behind = None
            if tracking_branch:
                ahead = list(repo.iter_commits(f'{tracking_branch}..HEAD'))
                behind = list(repo.iter_commits(f'HEAD..{tracking_branch}'))
                ahead_behind = {
                    "ahead": len(ahead),
                    "behind": len(behind)
                }

            return {
                "success": True,
                "current_branch": current_branch,
                "modified_files": modified_files,
                "staged_files": staged_files,
                "untracked_files": untracked_files,
                "is_dirty": repo.is_dirty(),
                "ahead_behind": ahead_behind,
                "summary": self._format_status_summary(
                    len(modified_files),
                    len(staged_files),
                    len(untracked_files)
                )
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def git_diff(
        self,
        file_path: Optional[str] = None,
        staged: bool = False
    ) -> Dict[str, any]:
        """
        Get diff of changes.

        Args:
            file_path: Optional specific file to diff
            staged: Show staged changes instead of unstaged

        Returns:
            Dictionary with diff information
        """
        try:
            repo = self.repo

            if staged:
                # Diff between staged and HEAD
                diff_index = repo.index.diff("HEAD")
            else:
                # Diff between working tree and index
                diff_index = repo.index.diff(None)

            # Filter by file if specified
            if file_path:
                diff_index = [d for d in diff_index if d.a_path == file_path]

            if not diff_index:
                return {
                    "success": True,
                    "diff": "",
                    "message": "No changes to show"
                }

            # Generate diff text
            diff_text = ""
            for diff_item in diff_index:
                diff_text += diff_item.diff.decode('utf-8', errors='replace')

            return {
                "success": True,
                "diff": diff_text,
                "files_changed": len(diff_index),
                "staged": staged
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def git_add(
        self,
        file_paths: Optional[List[str]] = None,
        all_files: bool = False
    ) -> Dict[str, any]:
        """
        Stage files for commit.

        Args:
            file_paths: List of file paths to stage
            all_files: Stage all modified and untracked files

        Returns:
            Dictionary with operation result
        """
        try:
            repo = self.repo

            if all_files:
                # Add all files
                repo.git.add(A=True)
                staged_files = "all files"
            elif file_paths:
                # Add specific files
                repo.index.add(file_paths)
                staged_files = file_paths
            else:
                return {
                    "success": False,
                    "error": "Must specify file_paths or set all_files=True"
                }

            return {
                "success": True,
                "operation": "staged",
                "files": staged_files
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def git_commit(
        self,
        message: str,
        file_paths: Optional[List[str]] = None,
        auto_stage: bool = True
    ) -> Dict[str, any]:
        """
        Create a git commit.

        Args:
            message: Commit message
            file_paths: Optional list of files to commit
            auto_stage: Automatically stage files before committing

        Returns:
            Dictionary with commit information
        """
        try:
            repo = self.repo

            # Stage files if specified
            if file_paths and auto_stage:
                await self.git_add(file_paths=file_paths)
            elif auto_stage and not file_paths:
                # Check if there are unstaged changes
                if repo.is_dirty(untracked_files=False):
                    # Stage modified files
                    repo.git.add(u=True)

            # Check if there's anything to commit
            if not repo.index.diff("HEAD") and not repo.untracked_files:
                return {
                    "success": False,
                    "error": "Nothing to commit (working tree clean)"
                }

            # Create commit
            commit = repo.index.commit(message)

            return {
                "success": True,
                "operation": "committed",
                "commit_hash": commit.hexsha[:7],
                "commit_message": message,
                "files_changed": len(commit.stats.files),
                "author": str(commit.author),
                "timestamp": commit.committed_datetime.isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def smart_commit(
        self,
        file_paths: Optional[List[str]] = None,
        custom_message: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Smart commit with auto-generated message.

        Args:
            file_paths: Optional list of files to commit
            custom_message: Optional custom message (overrides auto-generation)

        Returns:
            Dictionary with commit information
        """
        try:
            repo = self.repo

            # Get changes
            status = await self.git_status()
            if not status["success"]:
                return status

            if not status["is_dirty"]:
                return {
                    "success": False,
                    "error": "Nothing to commit"
                }

            # Generate commit message if not provided
            if custom_message:
                message = custom_message
            else:
                message = await self._generate_commit_message(status)

            # Commit
            return await self.git_commit(
                message=message,
                file_paths=file_paths,
                auto_stage=True
            )

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def create_branch(
        self,
        branch_name: str,
        checkout: bool = True
    ) -> Dict[str, any]:
        """
        Create a new branch.

        Args:
            branch_name: Name of the new branch
            checkout: Whether to checkout the new branch

        Returns:
            Dictionary with operation result
        """
        try:
            repo = self.repo

            # Check if branch already exists
            if branch_name in repo.heads:
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists"
                }

            # Create branch
            new_branch = repo.create_head(branch_name)

            if checkout:
                new_branch.checkout()

            return {
                "success": True,
                "operation": "created" + (" and checked out" if checkout else ""),
                "branch_name": branch_name,
                "current_branch": repo.active_branch.name
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def switch_branch(self, branch_name: str) -> Dict[str, any]:
        """
        Switch to a different branch.

        Args:
            branch_name: Name of the branch to switch to

        Returns:
            Dictionary with operation result
        """
        try:
            repo = self.repo

            # Check if branch exists
            if branch_name not in repo.heads:
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' does not exist"
                }

            # Check for uncommitted changes
            if repo.is_dirty():
                return {
                    "success": False,
                    "error": "Uncommitted changes. Please commit or stash them first."
                }

            # Switch branch
            repo.heads[branch_name].checkout()

            return {
                "success": True,
                "operation": "switched",
                "current_branch": branch_name
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_commit_history(
        self,
        max_count: int = 10,
        file_path: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get commit history.

        Args:
            max_count: Maximum number of commits to retrieve
            file_path: Optional filter by file path

        Returns:
            Dictionary with commit history
        """
        try:
            repo = self.repo

            # Get commits
            if file_path:
                commits = list(repo.iter_commits(paths=file_path, max_count=max_count))
            else:
                commits = list(repo.iter_commits(max_count=max_count))

            commit_list = []
            for commit in commits:
                commit_list.append({
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                    "files_changed": len(commit.stats.files)
                })

            return {
                "success": True,
                "commits": commit_list,
                "count": len(commit_list)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _format_status_summary(
        self,
        modified: int,
        staged: int,
        untracked: int
    ) -> str:
        """Format a human-readable status summary."""
        parts = []

        if staged > 0:
            parts.append(f"{staged} staged")
        if modified > 0:
            parts.append(f"{modified} modified")
        if untracked > 0:
            parts.append(f"{untracked} untracked")

        if not parts:
            return "Working tree clean"

        return ", ".join(parts)

    async def _generate_commit_message(self, status: Dict) -> str:
        """
        Generate a conventional commit message based on changes.

        Args:
            status: Git status dictionary

        Returns:
            Generated commit message
        """
        # Analyze changed files
        all_files = (
            status.get("modified_files", []) +
            status.get("staged_files", []) +
            status.get("untracked_files", [])
        )

        # Determine commit type
        commit_type = "chore"
        scope = ""

        # Simple heuristics
        if any("test" in f for f in all_files):
            commit_type = "test"
        elif any(f.endswith(('.md', '.txt')) for f in all_files):
            commit_type = "docs"
        elif any("fix" in f.lower() or "bug" in f.lower() for f in all_files):
            commit_type = "fix"
        elif len(status.get("untracked_files", [])) > len(status.get("modified_files", [])):
            commit_type = "feat"
        else:
            commit_type = "refactor"

        # Generate message
        file_count = len(all_files)
        if file_count == 1:
            file_desc = f"Update {Path(all_files[0]).name}"
        elif file_count <= 3:
            file_desc = f"Update {', '.join(Path(f).name for f in all_files[:3])}"
        else:
            file_desc = f"Update {file_count} files"

        return f"{commit_type}: {file_desc}"


# Global instance
git_ops = GitOperations()
