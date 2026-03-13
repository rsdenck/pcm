"""
LDAP authentication service for admin users.

This module provides LDAP integration for native admin authentication,
supporting both local and LDAP-based authentication in a hybrid model.
"""

import logging
import ldap
import ldap.modlist as modlist
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LDAPUser:
    """Represents an LDAP user."""
    username: str
    email: str
    full_name: str
    distinguished_name: str
    groups: List[str]
    attributes: Dict[str, Any]


class LDAPServiceError(Exception):
    """Base exception for LDAP service errors."""
    pass


class LDAPConnectionError(LDAPServiceError):
    """Raised when LDAP connection fails."""
    pass


class LDAPAuthenticationError(LDAPServiceError):
    """Raised when LDAP authentication fails."""
    pass


class LDAPService:
    """
    LDAP authentication service for admin users.
    
    Provides methods for:
    - Connecting to LDAP server
    - Authenticating users
    - Searching for users and groups
    - Syncing user information
    """
    
    def __init__(
        self,
        server_uri: str,
        bind_dn: str,
        bind_password: str,
        base_dn: str,
        user_search_filter: str = "(uid={username})",
        group_search_filter: str = "(cn=*)",
        timeout: int = 10
    ):
        """
        Initialize LDAP service.
        
        Args:
            server_uri: LDAP server URI (e.g., ldap://ldap.example.com:389)
            bind_dn: Distinguished name for binding
            bind_password: Password for binding
            base_dn: Base distinguished name for searches
            user_search_filter: Filter for user searches
            group_search_filter: Filter for group searches
            timeout: Connection timeout in seconds
        """
        self.server_uri = server_uri
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.base_dn = base_dn
        self.user_search_filter = user_search_filter
        self.group_search_filter = group_search_filter
        self.timeout = timeout
        self.connection: Optional[ldap.ldapobject.LDAPObject] = None
    
    def connect(self) -> None:
        """
        Connect to LDAP server.
        
        Raises:
            LDAPConnectionError: If connection fails
        """
        try:
            ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            self.connection = ldap.initialize(self.server_uri)
            self.connection.set_option(ldap.OPT_REFERRALS, 0)
            self.connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            
            # Bind with service account
            self.connection.simple_bind_s(self.bind_dn, self.bind_password)
            logger.info(f"Connected to LDAP server: {self.server_uri}")
            
        except ldap.CONNECT_ERROR as e:
            logger.error(f"Failed to connect to LDAP server: {e}")
            raise LDAPConnectionError(f"Failed to connect to LDAP server: {str(e)}")
        except ldap.INVALID_CREDENTIALS as e:
            logger.error(f"Invalid LDAP credentials: {e}")
            raise LDAPConnectionError(f"Invalid LDAP credentials: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected LDAP connection error: {e}")
            raise LDAPConnectionError(f"Unexpected LDAP connection error: {str(e)}")
    
    def disconnect(self) -> None:
        """Disconnect from LDAP server."""
        if self.connection:
            try:
                self.connection.unbind_s()
                logger.info("Disconnected from LDAP server")
            except Exception as e:
                logger.error(f"Error disconnecting from LDAP: {e}")
            finally:
                self.connection = None
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[LDAPUser]]:
        """
        Authenticate a user against LDAP.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Tuple of (success, user_info)
            
        Raises:
            LDAPAuthenticationError: If authentication fails
        """
        try:
            if not self.connection:
                self.connect()
            
            # Search for user
            search_filter = self.user_search_filter.format(username=username)
            results = self.connection.search_s(
                self.base_dn,
                ldap.SCOPE_SUBTREE,
                search_filter,
                ['*']
            )
            
            if not results or len(results) == 0:
                logger.warning(f"User not found in LDAP: {username}")
                raise LDAPAuthenticationError(f"User not found: {username}")
            
            # Get user DN
            user_dn, user_attrs = results[0]
            
            if not user_dn:
                raise LDAPAuthenticationError(f"Invalid user DN for: {username}")
            
            # Try to bind as user
            try:
                user_connection = ldap.initialize(self.server_uri)
                user_connection.set_option(ldap.OPT_REFERRALS, 0)
                user_connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
                user_connection.simple_bind_s(user_dn, password)
                user_connection.unbind_s()
                
                logger.info(f"Successfully authenticated user: {username}")
                
                # Extract user information
                ldap_user = self._extract_user_info(user_dn, user_attrs)
                return True, ldap_user
                
            except ldap.INVALID_CREDENTIALS:
                logger.warning(f"Invalid credentials for user: {username}")
                raise LDAPAuthenticationError(f"Invalid credentials for user: {username}")
        
        except LDAPAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            raise LDAPAuthenticationError(f"Error authenticating user: {str(e)}")
    
    def search_users(self, search_filter: Optional[str] = None) -> List[LDAPUser]:
        """
        Search for users in LDAP.
        
        Args:
            search_filter: Optional custom search filter
            
        Returns:
            List of LDAP users
        """
        try:
            if not self.connection:
                self.connect()
            
            filter_str = search_filter or self.user_search_filter.replace("{username}", "*")
            results = self.connection.search_s(
                self.base_dn,
                ldap.SCOPE_SUBTREE,
                filter_str,
                ['*']
            )
            
            users = []
            for user_dn, user_attrs in results:
                if user_dn:
                    user = self._extract_user_info(user_dn, user_attrs)
                    users.append(user)
            
            return users
        
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_user_groups(self, username: str) -> List[str]:
        """
        Get groups for a user.
        
        Args:
            username: Username to get groups for
            
        Returns:
            List of group names
        """
        try:
            if not self.connection:
                self.connect()
            
            # Search for user
            search_filter = self.user_search_filter.format(username=username)
            results = self.connection.search_s(
                self.base_dn,
                ldap.SCOPE_SUBTREE,
                search_filter,
                ['memberOf']
            )
            
            if not results:
                return []
            
            user_dn, user_attrs = results[0]
            
            # Extract group names from memberOf attribute
            groups = []
            if b'memberOf' in user_attrs:
                for group_dn in user_attrs[b'memberOf']:
                    group_name = self._extract_cn_from_dn(group_dn.decode('utf-8'))
                    if group_name:
                        groups.append(group_name)
            
            return groups
        
        except Exception as e:
            logger.error(f"Error getting user groups: {e}")
            return []
    
    def _extract_user_info(self, user_dn: str, user_attrs: Dict[str, List[bytes]]) -> LDAPUser:
        """
        Extract user information from LDAP attributes.
        
        Args:
            user_dn: User's distinguished name
            user_attrs: User's LDAP attributes
            
        Returns:
            LDAPUser object
        """
        def get_attr(key: str, default: str = "") -> str:
            if key.encode() in user_attrs:
                value = user_attrs[key.encode()]
                if isinstance(value, list) and len(value) > 0:
                    return value[0].decode('utf-8')
            return default
        
        username = get_attr('uid', get_attr('sAMAccountName', 'unknown'))
        email = get_attr('mail', f"{username}@example.com")
        full_name = get_attr('cn', get_attr('displayName', username))
        
        # Extract groups
        groups = []
        if b'memberOf' in user_attrs:
            for group_dn in user_attrs[b'memberOf']:
                group_name = self._extract_cn_from_dn(group_dn.decode('utf-8'))
                if group_name:
                    groups.append(group_name)
        
        return LDAPUser(
            username=username,
            email=email,
            full_name=full_name,
            distinguished_name=user_dn,
            groups=groups,
            attributes={k.decode('utf-8'): v for k, v in user_attrs.items()}
        )
    
    @staticmethod
    def _extract_cn_from_dn(dn: str) -> Optional[str]:
        """
        Extract CN (Common Name) from a distinguished name.
        
        Args:
            dn: Distinguished name
            
        Returns:
            Common name or None
        """
        try:
            parts = dn.split(',')
            for part in parts:
                if part.strip().startswith('cn='):
                    return part.strip()[3:]
        except Exception:
            pass
        return None
