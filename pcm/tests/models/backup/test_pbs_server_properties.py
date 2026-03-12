"""
Property-based tests for PBS server model.

**Validates: Requirements 1.2**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus


class TestPBSServerProperties:
    """Property-based tests for PBS server model."""

    @given(
        name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc')), min_size=1, max_size=50),
        hostname=st.sampled_from([
            "pbs.example.com", "backup.local", "server.domain.org", 
            "test.backup.net", "pbs1.datacenter.com", "backup-server.test.local"
        ]),
        port=st.integers(min_value=1, max_value=65535),
        api_token_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=50),
        api_token_secret=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=10, max_size=50),
        datacenter=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc')), min_size=1, max_size=50),
        verify_ssl=st.booleans(),
        timeout=st.integers(min_value=1, max_value=300),
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_pbs_server_connection_validation_property(
        self, name, hostname, port, api_token_id, api_token_secret, datacenter, verify_ssl, timeout
    ):
        """
        **Property 1: PBS server connection validation**
        **Validates: Requirements 1.2**
        
        Property: For any valid PBS server configuration, the connection URL should be 
        properly formatted and the server should maintain consistent connection properties.
        """
        # Create PBS server instance
        server = PBSServer(
            name=name,
            hostname=hostname,
            port=port,
            api_token_id=api_token_id,
            api_token_secret=api_token_secret,
            datacenter=datacenter,
            verify_ssl=verify_ssl,
            timeout=timeout
        )
        
        # Property 1a: Connection URL format consistency
        expected_protocol = "https" if verify_ssl else "http"
        expected_url = f"{expected_protocol}://{hostname}:{port}"
        assert server.connection_url == expected_url
        
        # Property 1b: Server properties are preserved
        assert server.name == name
        assert server.hostname == hostname
        assert server.port == port
        assert server.api_token_id == api_token_id
        assert server.api_token_secret == api_token_secret
        assert server.datacenter == datacenter
        assert server.verify_ssl == verify_ssl
        assert server.timeout == timeout
        
        # Property 1c: Default status and health state (handle SQLAlchemy defaults)
        # When created without database session, defaults may not be applied
        if server.status is not None:
            assert server.status == ServerStatus.OFFLINE
        if server.error_count is not None:
            assert server.error_count == 0
        assert server.is_healthy is False
        
        # Property 1d: Connection URL is always valid format
        assert "://" in server.connection_url
        assert server.connection_url.startswith(("http://", "https://"))
        assert hostname in server.connection_url
        assert str(port) in server.connection_url

    @given(
        server_data=st.fixed_dictionaries({
            'name': st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc')), min_size=1, max_size=50),
            'hostname': st.sampled_from([
                "pbs.example.com", "backup.local", "server.domain.org", 
                "test.backup.net", "pbs1.datacenter.com", "backup-server.test.local"
            ]),
            'port': st.integers(min_value=1, max_value=65535),
            'api_token_id': st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=50),
            'api_token_secret': st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=10, max_size=50),
            'datacenter': st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc')), min_size=1, max_size=50),
            'verify_ssl': st.booleans(),
            'timeout': st.integers(min_value=1, max_value=300),
        })
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_pbs_server_status_transitions_property(self, server_data):
        """
        **Property 1: PBS server connection validation - Status transitions**
        **Validates: Requirements 1.2**
        
        Property: Server status transitions should maintain consistency and 
        health status should reflect the current server state.
        """
        server = PBSServer(**server_data)
        
        # Initialize defaults if not set by SQLAlchemy
        if server.status is None:
            server.status = ServerStatus.OFFLINE
        if server.error_count is None:
            server.error_count = 0
        
        # Property: Initial state consistency
        assert server.status == ServerStatus.OFFLINE
        assert server.is_healthy is False
        
        # Property: Online transition updates health
        server.mark_online(version="2.4.0", capabilities={"encryption": True})
        assert server.status == ServerStatus.ONLINE
        assert server.is_healthy is True
        assert server.error_count == 0
        assert server.last_error is None
        assert server.version == "2.4.0"
        assert server.capabilities == {"encryption": True}
        
        # Property: Offline transition maintains error state
        error_msg = "Connection timeout"
        server.mark_offline(error_msg)
        assert server.status == ServerStatus.OFFLINE
        assert server.is_healthy is False
        assert server.last_error == error_msg
        assert server.error_count == 1
        
        # Property: Multiple offline calls increment error count
        server.mark_offline("Another error")
        assert server.error_count == 2
        
        # Property: Online transition resets error state
        server.mark_online()
        assert server.error_count == 0
        assert server.last_error is None

    @given(
        ssl_enabled=st.booleans(),
        port=st.integers(min_value=1, max_value=65535),
        hostname=st.sampled_from([
            "pbs.example.com", "backup.local", "server.domain.org", 
            "test.backup.net", "pbs1.datacenter.com"
        ])
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_connection_url_protocol_consistency_property(self, ssl_enabled, port, hostname):
        """
        **Property 1: PBS server connection validation - URL protocol consistency**
        **Validates: Requirements 1.2**
        
        Property: Connection URL protocol should always match SSL verification setting.
        """
        server = PBSServer(
            name="test-server",
            hostname=hostname,
            port=port,
            api_token_id="test-token",
            api_token_secret="test-secret",
            datacenter="test-dc",
            verify_ssl=ssl_enabled
        )
        
        # Property: Protocol matches SSL setting
        if ssl_enabled:
            assert server.connection_url.startswith("https://")
        else:
            assert server.connection_url.startswith("http://")
        
        # Property: URL contains all required components
        assert hostname in server.connection_url
        assert str(port) in server.connection_url
        
        # Property: URL format is consistent
        expected_url = f"{'https' if ssl_enabled else 'http'}://{hostname}:{port}"
        assert server.connection_url == expected_url

    @given(
        status=st.sampled_from(list(ServerStatus))
    )
    def test_health_status_consistency_property(self, status):
        """
        **Property 1: PBS server connection validation - Health status consistency**
        **Validates: Requirements 1.2**
        
        Property: Health status should be consistent with server status.
        """
        server = PBSServer(
            name="test-server",
            hostname="test.example.com",
            port=8007,
            api_token_id="test-token",
            api_token_secret="test-secret",
            datacenter="test-dc"
        )
        
        server.status = status
        
        # Property: Only ONLINE status is considered healthy
        if status == ServerStatus.ONLINE:
            assert server.is_healthy is True
        else:
            assert server.is_healthy is False

    @given(
        error_messages=st.lists(
            st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()),
            min_size=1,
            max_size=10
        )
    )
    def test_error_tracking_consistency_property(self, error_messages):
        """
        **Property 1: PBS server connection validation - Error tracking consistency**
        **Validates: Requirements 1.2**
        
        Property: Error tracking should maintain consistent state and count.
        """
        server = PBSServer(
            name="test-server",
            hostname="test.example.com",
            port=8007,
            api_token_id="test-token",
            api_token_secret="test-secret",
            datacenter="test-dc"
        )
        
        # Initialize defaults if not set by SQLAlchemy
        if server.error_count is None:
            server.error_count = 0
        
        initial_error_count = server.error_count
        
        # Property: Error count increases with each offline call with error
        for i, error_msg in enumerate(error_messages, 1):
            server.mark_offline(error_msg)
            assert server.error_count == initial_error_count + i
            assert server.last_error == error_msg
            assert server.status == ServerStatus.OFFLINE
            assert server.is_healthy is False
        
        # Property: Online transition resets error state
        server.mark_online()
        assert server.error_count == 0
        assert server.last_error is None
        assert server.status == ServerStatus.ONLINE
        assert server.is_healthy is True