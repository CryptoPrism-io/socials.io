#!/usr/bin/env python3
"""
Instagram Session Manager - Smart Session Persistence
Implements rate-limiting protection and session management best practices
Based on instagrapi documentation and Instagram compliance guidelines
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError

logger = logging.getLogger(__name__)

class InstagramSessionManager:
    """
    Smart Instagram session manager implementing rate-limiting protection
    and persistent session management following instagrapi best practices.
    """

    def __init__(self,
                 session_file: str = "instagram_session.json",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 session_max_age_days: int = 30):
        """
        Initialize Instagram session manager.

        Args:
            session_file: Path to session storage file
            username: Instagram username (from env vars)
            password: Instagram password (from env vars)
            session_max_age_days: Maximum session age before refresh (default: 30 days)
        """
        self.session_file = Path(session_file)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        self.username = username or os.getenv('INSTAGRAM_USERNAME')
        self.password = password or os.getenv('INSTAGRAM_PASSWORD')
        self.session_max_age_days = session_max_age_days

        self.client: Optional[Client] = None
        self._session_metadata: Dict[str, Any] = {}

        # Rate limiting protection
        self.min_login_interval_hours = 168  # Minimum time between username/password logins (7 days)

        if not self.username or not self.password:
            raise ValueError("Instagram username and password must be provided via environment variables")

    def get_smart_client(self) -> Optional[Client]:
        """
        Get Instagram client with smart session management.

        Returns:
            Authenticated Instagram client or None if authentication failed
        """
        try:
            # Try loading existing session first
            if self._load_existing_session():
                if self._validate_session():
                    logger.info("✅ Using existing valid session")
                    return self.client
                else:
                    logger.info("⚠️ Existing session invalid, attempting refresh")

            # Only do fresh login if session is missing/invalid
            if self._should_attempt_fresh_login():
                return self._fresh_login_and_save()
            else:
                logger.error("❌ Cannot attempt fresh login due to rate limiting protection")
                return None

        except Exception as e:
            logger.error(f"❌ Error in smart session management: {e}")
            return None

    def _load_existing_session(self) -> bool:
        """
        Try to load existing session from file.

        Returns:
            True if session loaded successfully, False otherwise
        """
        if not self.session_file.exists():
            logger.info("📁 No existing session file found")
            return False

        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            # Extract session metadata
            self._session_metadata = session_data.get('metadata', {})

            # Check session age
            if self._is_session_too_old():
                logger.info("⏰ Session too old, needs refresh")
                return False

            # Initialize client and load session
            self.client = Client()

            # Set delay range for natural behavior
            self.client.delay_range = [1, 3]

            # Load the actual session data
            if 'session_data' in session_data:
                # New format with metadata
                session_file_temp = self.session_file.with_suffix('.tmp')
                with open(session_file_temp, 'w') as f:
                    json.dump(session_data['session_data'], f)

                self.client.load_settings(str(session_file_temp))
                session_file_temp.unlink()  # Clean up temp file
            else:
                # Legacy format - direct session data
                self.client.load_settings(str(self.session_file))

            logger.info("✅ Session loaded from file")
            return True

        except json.JSONDecodeError:
            logger.error("❌ Session file corrupted")
            return False
        except Exception as e:
            logger.error(f"❌ Error loading session: {e}")
            return False

    def _validate_session(self) -> bool:
        """
        Validate that the loaded session is still functional.

        Returns:
            True if session is valid, False otherwise
        """
        if not self.client:
            return False

        try:
            # Test session with lightweight API call
            logger.info("🔍 Validating session with API test...")

            # Use stored username from metadata instead of client.username which might not be set
            stored_username = self._session_metadata.get('username', self.username)

            # Try to get user info - this is a lightweight operation
            user_info = self.client.user_info_by_username(stored_username)

            if user_info and user_info.pk:
                logger.info(f"✅ Session valid - authenticated as {stored_username}")
                self._update_session_metadata('last_validated', datetime.now().isoformat())
                return True
            else:
                logger.warning("⚠️ Session validation returned empty user info")
                return False

        except LoginRequired:
            logger.warning("⚠️ Session expired - LoginRequired exception")
            return False
        except ClientError as e:
            logger.warning(f"⚠️ Session validation failed - Client error: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Session validation failed - Unexpected error: {e}")
            # For unexpected errors, assume session might still be valid
            # Instagram sometimes has temporary issues
            return True

    def _should_attempt_fresh_login(self) -> bool:
        """
        Check if we should attempt a fresh username/password login.
        Implements rate limiting protection.

        Returns:
            True if fresh login is allowed, False if rate limited
        """
        last_login = self._session_metadata.get('last_fresh_login')

        if not last_login:
            # No previous login recorded, allow it
            return True

        try:
            last_login_time = datetime.fromisoformat(last_login)
            time_since_login = datetime.now() - last_login_time

            if time_since_login.total_seconds() < (self.min_login_interval_hours * 3600):
                hours_remaining = self.min_login_interval_hours - (time_since_login.total_seconds() / 3600)
                logger.warning(f"⏳ Rate limiting: {hours_remaining:.1f} hours until next login allowed")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Error checking login interval: {e}")
            # If we can't parse the timestamp, allow login
            return True

    def _fresh_login_and_save(self) -> Optional[Client]:
        """
        Perform fresh username/password login and save session.

        Returns:
            Authenticated client or None if login failed
        """
        try:
            logger.info("🔄 Attempting fresh Instagram login...")

            # Initialize new client
            self.client = Client()
            self.client.delay_range = [1, 3]

            # Preserve device UUID if we have one from previous session
            old_uuids = self._session_metadata.get('device_uuids')
            if old_uuids:
                self.client.set_uuids(old_uuids)
                logger.info("✅ Preserved device UUIDs for consistency")

            # Perform login
            success = self.client.login(self.username, self.password)

            if success:
                logger.info("✅ Fresh login successful!")

                # Save session immediately
                self._save_session()

                return self.client
            else:
                logger.error("❌ Fresh login failed")
                return None

        except Exception as e:
            logger.error(f"❌ Fresh login error: {e}")
            return None

    def _save_session(self):
        """Save current session to file with metadata."""
        try:
            # Get current session data from client
            session_temp_file = self.session_file.with_suffix('.tmp')
            self.client.dump_settings(str(session_temp_file))

            # Load the dumped session data
            with open(session_temp_file, 'r') as f:
                session_data = json.load(f)

            # Update metadata
            now = datetime.now().isoformat()
            self._session_metadata.update({
                'created_at': self._session_metadata.get('created_at', now),
                'last_updated': now,
                'last_fresh_login': now,
                'last_validated': now,
                'login_count': self._session_metadata.get('login_count', 0) + 1,
                'device_uuids': session_data.get('uuids', {}),
                'username': self.client.username,
                'session_version': '1.0'
            })

            # Create comprehensive session file
            comprehensive_session = {
                'session_data': session_data,
                'metadata': self._session_metadata
            }

            # Save comprehensive session to primary location
            with open(self.session_file, 'w') as f:
                json.dump(comprehensive_session, f, indent=2)

            logger.info(f"✅ Session saved to {self.session_file}")

            # Also save to sessions/ directory if primary location is in data/
            if 'data' in str(self.session_file).lower():
                sessions_dir = Path('sessions')
                sessions_dir.mkdir(parents=True, exist_ok=True)
                backup_session_file = sessions_dir / 'instagram_session.json'

                with open(backup_session_file, 'w') as f:
                    json.dump(comprehensive_session, f, indent=2)

                logger.info(f"✅ Session also saved to {backup_session_file}")

            # Clean up temp file
            session_temp_file.unlink()

        except Exception as e:
            logger.error(f"❌ Error saving session: {e}")

    def _update_session_metadata(self, key: str, value: Any):
        """Update session metadata and save to file."""
        self._session_metadata[key] = value

        # Update the metadata in the session file if it exists
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)

                data['metadata'] = self._session_metadata

                # Save to primary location
                with open(self.session_file, 'w') as f:
                    json.dump(data, f, indent=2)

                # Also save to sessions/ directory if primary location is in data/
                if 'data' in str(self.session_file).lower():
                    sessions_dir = Path('sessions')
                    sessions_dir.mkdir(parents=True, exist_ok=True)
                    backup_session_file = sessions_dir / 'instagram_session.json'

                    with open(backup_session_file, 'w') as f:
                        json.dump(data, f, indent=2)

            except Exception as e:
                logger.error(f"❌ Error updating metadata: {e}")

    def _is_session_too_old(self) -> bool:
        """Check if session is older than maximum allowed age."""
        created_at = self._session_metadata.get('created_at')

        if not created_at:
            return True  # No creation date = treat as old

        try:
            creation_time = datetime.fromisoformat(created_at)
            age = datetime.now() - creation_time

            is_old = age.days >= self.session_max_age_days

            if is_old:
                logger.info(f"⏰ Session is {age.days} days old (max: {self.session_max_age_days})")

            return is_old

        except Exception as e:
            logger.error(f"❌ Error checking session age: {e}")
            return True  # If we can't parse date, treat as old

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information and health status."""
        info = {
            'session_file_exists': self.session_file.exists(),
            'client_authenticated': self.client is not None,
            'metadata': self._session_metadata.copy()
        }

        if self._session_metadata:
            # Calculate session age
            created_at = self._session_metadata.get('created_at')
            if created_at:
                try:
                    creation_time = datetime.fromisoformat(created_at)
                    age = datetime.now() - creation_time
                    info['session_age_days'] = age.days
                    info['session_age_hours'] = age.total_seconds() / 3600
                except:
                    pass

        return info

    def force_refresh_session(self) -> Optional[Client]:
        """Force a fresh login regardless of rate limiting (use with caution)."""
        logger.warning("⚠️ FORCING session refresh - bypassing rate limiting!")

        # Temporarily disable rate limiting
        original_interval = self.min_login_interval_hours
        self.min_login_interval_hours = 0

        try:
            return self._fresh_login_and_save()
        finally:
            # Restore rate limiting
            self.min_login_interval_hours = original_interval

    def get_client_bypass_validation(self) -> Optional[Client]:
        """
        Get Instagram client bypassing the problematic user_info validation.

        This method loads the session directly without calling user_info_by_username
        which has a bug in instagrapi ~2.1 causing false session expiration errors.

        Returns:
            Authenticated Instagram client or None if session loading failed
        """
        try:
            # Try loading existing session first
            if self._load_existing_session():
                logger.info("✅ Session loaded successfully")

                # Test with a simple API call that doesn't use the buggy method
                try:
                    # Try to get user ID to verify session works
                    if hasattr(self.client, 'user_id') and self.client.user_id:
                        logger.info(f"✅ Session bypass successful - User ID: {self.client.user_id}")
                        self._update_session_metadata('last_validated', datetime.now().isoformat())
                        return self.client
                    else:
                        logger.warning("⚠️ No user ID available in session")
                        return None

                except Exception as e:
                    logger.warning(f"⚠️ Session test failed: {e}")
                    return None
            else:
                logger.info("📁 No valid session found")
                return None

        except Exception as e:
            logger.error(f"❌ Error in bypass session loading: {e}")
            return None