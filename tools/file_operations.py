"""File operations tools for reading and writing files."""
import os
import shutil
import difflib
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import aiofiles


class FileOperations:
    """Tools for file manipulation with safety features."""

    def __init__(self, backup_dir: str = ".agent_backup"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    async def write_file(
        self,
        file_path: str,
        content: str,
        create_backup: bool = True
    ) -> Dict[str, any]:
        """
        Write content to a file (create or overwrite).

        Args:
            file_path: Path to the file
            content: Content to write
            create_backup: Whether to backup existing file

        Returns:
            Dictionary with operation result
        """
        try:
            path = Path(file_path)

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Backup existing file
            backup_path = None
            if path.exists() and create_backup:
                backup_path = await self._create_backup(path)

            # Write to temporary file first (atomic write)
            temp_path = path.with_suffix(path.suffix + '.tmp')
            async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                await f.write(content)

            # Move temp file to target (atomic operation)
            temp_path.replace(path)

            return {
                "success": True,
                "file_path": str(path),
                "operation": "created" if not backup_path else "updated",
                "backup_path": str(backup_path) if backup_path else None,
                "size": len(content),
                "lines": content.count('\n') + 1
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    async def read_file(self, file_path: str) -> Dict[str, any]:
        """
        Read file content.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file content and metadata
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()

            return {
                "success": True,
                "file_path": str(path),
                "content": content,
                "size": len(content),
                "lines": content.count('\n') + 1
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    async def edit_file(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        create_backup: bool = True
    ) -> Dict[str, any]:
        """
        Edit file by replacing specific content.

        Args:
            file_path: Path to the file
            old_content: Content to replace
            new_content: New content
            create_backup: Whether to backup existing file

        Returns:
            Dictionary with operation result and diff
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            # Read current content
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                current_content = await f.read()

            # Check if old_content exists
            if old_content not in current_content:
                return {
                    "success": False,
                    "error": "Content to replace not found in file",
                    "hint": "Make sure old_content exactly matches the text in the file"
                }

            # Replace content
            updated_content = current_content.replace(old_content, new_content, 1)

            # Generate diff
            diff = self._generate_diff(
                current_content.splitlines(keepends=True),
                updated_content.splitlines(keepends=True),
                path.name
            )

            # Backup and write
            if create_backup:
                backup_path = await self._create_backup(path)

            # Write new content
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(updated_content)

            return {
                "success": True,
                "file_path": str(path),
                "operation": "edited",
                "diff": diff,
                "backup_path": str(backup_path) if create_backup else None,
                "changes": {
                    "lines_before": current_content.count('\n') + 1,
                    "lines_after": updated_content.count('\n') + 1
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    async def insert_code(
        self,
        file_path: str,
        line_number: int,
        code: str,
        create_backup: bool = True
    ) -> Dict[str, any]:
        """
        Insert code at a specific line number.

        Args:
            file_path: Path to the file
            line_number: Line number to insert after (1-indexed)
            code: Code to insert
            create_backup: Whether to backup existing file

        Returns:
            Dictionary with operation result
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            # Read lines
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()

            # Validate line number
            if line_number < 0 or line_number > len(lines):
                return {
                    "success": False,
                    "error": f"Invalid line number: {line_number} (file has {len(lines)} lines)"
                }

            # Insert code
            if not code.endswith('\n'):
                code += '\n'

            lines.insert(line_number, code)
            new_content = ''.join(lines)

            # Backup and write
            if create_backup:
                backup_path = await self._create_backup(path)

            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(new_content)

            return {
                "success": True,
                "file_path": str(path),
                "operation": "inserted",
                "inserted_at_line": line_number,
                "backup_path": str(backup_path) if create_backup else None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    async def delete_lines(
        self,
        file_path: str,
        start_line: int,
        end_line: int,
        create_backup: bool = True
    ) -> Dict[str, any]:
        """
        Delete a range of lines from a file.

        Args:
            file_path: Path to the file
            start_line: Starting line number (1-indexed, inclusive)
            end_line: Ending line number (1-indexed, inclusive)
            create_backup: Whether to backup existing file

        Returns:
            Dictionary with operation result
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            # Read lines
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()

            # Validate line numbers (convert to 0-indexed)
            if start_line < 1 or end_line > len(lines) or start_line > end_line:
                return {
                    "success": False,
                    "error": f"Invalid line range: {start_line}-{end_line} (file has {len(lines)} lines)"
                }

            # Delete lines
            deleted_lines = lines[start_line-1:end_line]
            del lines[start_line-1:end_line]
            new_content = ''.join(lines)

            # Backup and write
            if create_backup:
                backup_path = await self._create_backup(path)

            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(new_content)

            return {
                "success": True,
                "file_path": str(path),
                "operation": "deleted",
                "deleted_lines": f"{start_line}-{end_line}",
                "deleted_count": len(deleted_lines),
                "backup_path": str(backup_path) if create_backup else None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    async def _create_backup(self, file_path: Path) -> Path:
        """Create a timestamped backup of a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name

        # Copy file to backup
        await asyncio.to_thread(shutil.copy2, file_path, backup_path)

        return backup_path

    def _generate_diff(
        self,
        old_lines: List[str],
        new_lines: List[str],
        filename: str
    ) -> str:
        """Generate unified diff between two versions."""
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=''
        )
        return '\n'.join(diff)

    async def list_backups(self, file_path: Optional[str] = None) -> List[Dict]:
        """
        List available backups.

        Args:
            file_path: Optional filter by original file path

        Returns:
            List of backup information
        """
        backups = []

        for backup in self.backup_dir.glob("*.backup"):
            # Parse backup filename
            parts = backup.name.rsplit('.', 2)
            if len(parts) >= 3:
                original_name = parts[0]
                timestamp = parts[1]

                if file_path is None or original_name == Path(file_path).name:
                    backups.append({
                        "original_name": original_name,
                        "backup_path": str(backup),
                        "timestamp": timestamp,
                        "size": backup.stat().st_size
                    })

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)

        return backups

    async def restore_backup(
        self,
        backup_path: str,
        target_path: str
    ) -> Dict[str, any]:
        """
        Restore a file from backup.

        Args:
            backup_path: Path to backup file
            target_path: Path to restore to

        Returns:
            Dictionary with operation result
        """
        try:
            backup = Path(backup_path)
            target = Path(target_path)

            if not backup.exists():
                return {
                    "success": False,
                    "error": f"Backup not found: {backup_path}"
                }

            # Create backup of current file before restoring
            if target.exists():
                await self._create_backup(target)

            # Copy backup to target
            await asyncio.to_thread(shutil.copy2, backup, target)

            return {
                "success": True,
                "restored_to": str(target),
                "from_backup": str(backup)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
file_ops = FileOperations()
