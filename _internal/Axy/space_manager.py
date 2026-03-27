"""
Space Management Module for Axy
Prevents disk space exhaustion by managing data accumulation
"""
# ==============================================================================
# Copyright (c) 2026 Axo. All rights reserved.
# 
# This software is proprietary and confidential.
# Unauthorized copying, distribution, modification, or use of this file,
# via any medium, is strictly prohibited without the express written 
# consent of the developer.
# 
# AXY - Local Python Mentor
# ==============================================================================

import os
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from .paths import get_data_dir

logger = logging.getLogger(__name__)

class SpaceManager:
    """Manages disk space usage and prevents data accumulation issues."""

    def __init__(self, data_dir: str = None, max_total_mb: float = 100.0):
        self.data_dir = Path(data_dir) if data_dir else get_data_dir()
        self.max_total_mb = max_total_mb
        self.max_chat_files = 20  # Maximum saved chat files per user
        self.max_history_messages = 100  # Maximum messages in main chat history
        self.cleanup_interval_days = 7  # Run cleanup weekly
        self.archive_dir = self.data_dir / "archive"  # Archive old chats here

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def check_space_usage(self) -> Dict[str, Any]:
        """Check current space usage and return statistics."""
        if not self.data_dir.exists():
            return {"total_mb": 0, "files_count": 0, "needs_cleanup": False}

        total_size = 0
        files_info = []

        for file_path in self.data_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                files_info.append({
                    "path": str(file_path),
                    "size": size,
                    "modified": file_path.stat().st_mtime
                })

        total_mb = total_size / 1024 / 1024
        needs_cleanup = total_mb > self.max_total_mb

        return {
            "total_mb": round(total_mb, 2),
            "files_count": len(files_info),
            "max_allowed_mb": self.max_total_mb,
            "needs_cleanup": needs_cleanup,
            "usage_percent": round((total_mb / self.max_total_mb) * 100, 1)
        }

    def cleanup_old_data(self) -> Dict[str, Any]:
        """Perform cleanup of old/unnecessary data."""
        logger.info("Starting space cleanup...")
        stats = {"files_removed": 0, "space_freed_mb": 0, "errors": []}

        try:
            # 1. Clean up old chat history files (keep only recent ones)
            stats.update(self._cleanup_chat_files())

            # 2. Compress/truncate main chat histories
            stats.update(self._cleanup_main_history())

            # 3. Archive old user data if needed
            stats.update(self._cleanup_user_data())

            # 4. Remove temporary files
            stats.update(self._cleanup_temp_files())

        except Exception as e:
            logger.error(f"Space cleanup error: {e}")
            stats["errors"].append(str(e))

        logger.info(f"Space cleanup completed: {stats}")
        return stats

    def _cleanup_chat_files(self) -> Dict[str, Any]:
        """Clean up saved chat files with intelligent archiving."""
        stats = {"chat_files_removed": 0, "chat_files_archived": 0, "chat_space_freed": 0}

        chats_dir = self.data_dir / "chats"
        if not chats_dir.exists():
            return stats

        # Group files by user (assuming filename pattern: username_timestamp.json)
        user_files = {}
        for file_path in chats_dir.glob("*.json"):
            try:
                # Extract username from filename (everything before first underscore or space)
                filename = file_path.stem
                username = filename.split('_')[0].split(' ')[0]

                if username not in user_files:
                    user_files[username] = []
                user_files[username].append({
                    "path": file_path,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "filename": file_path.name
                })
            except Exception as e:
                logger.warning(f"Error parsing chat file {file_path}: {e}")

        # For each user, implement smart retention policy
        for username, files in user_files.items():
            if len(files) > self.max_chat_files:
                # Sort by modification time (newest first)
                files.sort(key=lambda x: x["modified"], reverse=True)

                # Keep the most recent files
                files_to_archive = files[self.max_chat_files:]

                # Archive older files instead of deleting
                for file_info in files_to_archive:
                    try:
                        # Create archive path (preserve original filename)
                        archive_path = self.archive_dir / file_info['filename']

                        # Move file to archive
                        file_info["path"].rename(archive_path)

                        stats["chat_files_archived"] += 1
                        stats["chat_space_freed"] += file_info["size"]  # Space freed in active directory

                        logger.info(f"Archived chat file: {file_info['path']} → {archive_path}")

                    except Exception as e:
                        logger.error(f"Failed to archive {file_info['path']}: {e}")
                        # Fallback: delete if archiving fails
                        try:
                            file_info["path"].unlink()
                            stats["chat_files_removed"] += 1
                            logger.info(f"Deleted chat file (archive failed): {file_info['path']}")
                        except Exception as e2:
                            logger.error(f"Failed to delete {file_info['path']}: {e2}")

        stats["chat_space_freed"] = round(stats["chat_space_freed"] / 1024 / 1024, 2)
        return stats

    def _cleanup_main_history(self) -> Dict[str, Any]:
        """Truncate main chat history files if they're too large."""
        stats = {"history_files_cleaned": 0, "history_space_saved": 0}

        history_file = self.data_dir / "chat_history.json"
        if not history_file.exists():
            return stats

        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            original_size = history_file.stat().st_size
            original_count = len(history)

            # Keep only recent messages
            if len(history) > self.max_history_messages:
                # Keep system messages + most recent conversation messages
                system_messages = [m for m in history if m.get("role") == "system"]
                conversation_messages = [m for m in history if m.get("role") != "system"]

                if len(conversation_messages) > self.max_history_messages:
                    conversation_messages = conversation_messages[-self.max_history_messages:]

                history = system_messages + conversation_messages

                # Write back the truncated history
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)

                new_size = history_file.stat().st_size
                stats["history_files_cleaned"] = 1
                stats["history_space_saved"] = round((original_size - new_size) / 1024 / 1024, 2)

                logger.info(f"Truncated chat history: {original_count} → {len(history)} messages")

        except Exception as e:
            logger.error(f"Failed to cleanup chat history: {e}")

        return stats

    def _cleanup_user_data(self) -> Dict[str, Any]:
        """Clean up old user data or archive inactive users."""
        stats = {"users_archived": 0, "user_space_saved": 0}

        users_file = self.data_dir / "users.json"
        if not users_file.exists():
            return stats

        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)

            # For now, just log user count - could implement archiving of inactive users
            active_users = len(users)
            logger.info(f"Active users: {active_users}")

            # Future: Archive users inactive for > 1 year
            # This would require adding last_activity timestamps

        except Exception as e:
            logger.error(f"Failed to cleanup user data: {e}")

        return stats

    def _cleanup_temp_files(self) -> Dict[str, Any]:
        """Remove temporary files and caches."""
        stats = {"temp_files_removed": 0, "temp_space_freed": 0}

        # Clean up __pycache__ directories
        for pycache_dir in self.data_dir.parent.rglob("__pycache__"):
            if pycache_dir.is_dir():
                try:
                    shutil.rmtree(pycache_dir)
                    logger.info(f"Removed cache directory: {pycache_dir}")
                except Exception as e:
                    logger.warning(f"Failed to remove cache dir {pycache_dir}: {e}")

        # Clean up any .tmp files in data directory
        for tmp_file in self.data_dir.rglob("*.tmp"):
            try:
                size = tmp_file.stat().st_size
                tmp_file.unlink()
                stats["temp_files_removed"] += 1
                stats["temp_space_freed"] += size
                logger.info(f"Removed temp file: {tmp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file {tmp_file}: {e}")

        stats["temp_space_freed"] = round(stats["temp_space_freed"] / 1024 / 1024, 2)
        return stats

    def get_user_chat_stats(self, username: str) -> Dict[str, Any]:
        """Get chat statistics for a specific user."""
        chats_dir = self.data_dir / "chats"
        archive_dir = self.data_dir / "archive"

        active_chats = []
        archived_chats = []

        # Count active chats
        if chats_dir.exists():
            for file_path in chats_dir.glob(f"{username}_*.json"):
                active_chats.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })

        # Count archived chats
        if archive_dir.exists():
            for file_path in archive_dir.glob(f"{username}_*.json"):
                archived_chats.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })

        return {
            "username": username,
            "active_chats": len(active_chats),
            "archived_chats": len(archived_chats),
            "total_chats": len(active_chats) + len(archived_chats),
            "active_size_mb": round(sum(c["size"] for c in active_chats) / 1024 / 1024, 2),
            "archived_size_mb": round(sum(c["size"] for c in archived_chats) / 1024 / 1024, 2),
            "max_allowed": self.max_chat_files
        }

    def restore_archived_chat(self, username: str, filename: str) -> bool:
        """Restore an archived chat back to active chats."""
        archive_path = self.archive_dir / filename
        active_path = self.data_dir / "chats" / filename

        if not archive_path.exists():
            return False

        # Check if we're at the limit
        user_stats = self.get_user_chat_stats(username)
        if user_stats["active_chats"] >= self.max_chat_files:
            return False  # Can't restore, at limit

        try:
            # Move from archive back to active
            archive_path.rename(active_path)
            logger.info(f"Restored archived chat: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore chat {filename}: {e}")
            return False

    def export_user_chats(self, username: str, export_dir: str = None) -> str:
        """Export all of a user's chats (active and archived) to a directory."""
        if export_dir is None:
            export_dir = f"user_{username}_chats_export"

        export_path = Path(export_dir)
        export_path.mkdir(exist_ok=True)

        chats_dir = self.data_dir / "chats"
        archive_dir = self.data_dir / "archive"

        exported_count = 0

        # Export active chats
        if chats_dir.exists():
            for file_path in chats_dir.glob(f"{username}_*.json"):
                try:
                    shutil.copy2(file_path, export_path / file_path.name)
                    exported_count += 1
                except Exception as e:
                    logger.error(f"Failed to export {file_path}: {e}")

        # Export archived chats
        if archive_dir.exists():
            for file_path in archive_dir.glob(f"{username}_*.json"):
                try:
                    shutil.copy2(file_path, export_path / file_path.name)
                    exported_count += 1
                except Exception as e:
                    logger.error(f"Failed to export {file_path}: {e}")

        return str(export_path.absolute())

    def cleanup_archive_if_needed(self) -> Dict[str, Any]:
        """Clean up very old archived chats if space is critically low."""
        stats = {"archived_files_removed": 0, "archive_space_freed": 0}

        # Only run if we're at 95%+ capacity
        usage = self.check_space_usage()
        if usage["usage_percent"] < 95:
            return stats

        logger.warning("Critical space usage, cleaning old archived chats")

        # Remove archived chats older than 90 days
        cutoff_time = datetime.now().timestamp() - (90 * 24 * 60 * 60)

        if self.archive_dir.exists():
            for file_path in self.archive_dir.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        stats["archived_files_removed"] += 1
                        stats["archive_space_freed"] += size
                        logger.info(f"Removed very old archived chat: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove archived chat {file_path}: {e}")

        stats["archive_space_freed"] = round(stats["archive_space_freed"] / 1024 / 1024, 2)
        return stats

    def get_space_warning(self) -> Optional[str]:
        """Get warning message if space usage is high."""
        usage = self.check_space_usage()

        if usage["usage_percent"] > 90:
            return f"⚠️ CRITICAL: Data directory using {usage['usage_percent']}% of allocated space ({usage['total_mb']}MB/{usage['max_allowed_mb']}MB)"
        elif usage["usage_percent"] > 75:
            return f"⚠️ WARNING: Data directory using {usage['usage_percent']}% of allocated space ({usage['total_mb']}MB/{usage['max_allowed_mb']}MB)"
        elif usage["needs_cleanup"]:
            return f"ℹ️ INFO: Data directory size ({usage['total_mb']}MB) exceeds recommended limit"

        return None

# Global space manager instance
space_manager = SpaceManager()
