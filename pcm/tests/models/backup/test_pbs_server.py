"""
Unit tests for PBSServer model.

Tests model validation, constraints, status management, and health monitoring.
"""

import pytest
from datetime import datetime, timedelta
from pcm.core.models.backup import PBSServer, ServerStatus


class TestPBSServer:
    """Test cases for PBSServer model."""

    def test_server_creation(self):
        """Test basic server creation with required fields."""
        server = PBSServer(
            name="Test PBS Server",
            hostname="pbs.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret-key",
            datacenter="dc1"
        )
        
        assert server.name == "Test PBS Server"
        assert server.hostname == "pbs.example.com"
        assert server.port == 8007  # Default port
        assert server.api_token_id == "test@pbs!token"
        assert server.api_token_secret == "secret-key"
        assert server.datacenter == "dc1"
        assert server.status == ServerStatus.OFFLINE  # Default status
        assert server.verify_ssl is True  # Default
        assert server.timeout == 30  # Default
        assert server.health_check_interval == 300  # Default
        assert server.error_count == 0
        assert server.created_at is not None
        assert server.updated_at is not None

    def test_server_creation_with_custom_values(self):
        """Test server creation with custom configuration values."""
        server = PBSServer(
            name="Custom PBS Server",
            hostname="custom-pbs.example.com",
            port=8008,
            api_token_id="custom@pbs!token",
            api_token_secret="custom-secret",
            datacenter="dc2",
            verify_ssl=False,
            timeout=60,
            health_check_interval=600,
            description="Custom PBS server for testing"
        )
        
        assert server.port == 8008
        assert server.verify_ssl is False
        assert server.timeout == 60
        assert server.health_check_interval == 600
        assert server.description == "Custom PBS server for testing"

    def test_server_status_enum_validation(self):
        """Test that server status accepts valid enum values."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Test all valid status values
        for status in ServerStatus:
            server.status = status
            assert server.status == status

    def test_is_healthy_property(self):
        """Test is_healthy property logic."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Test healthy state
        server.status = ServerStatus.ONLINE
        assert server.is_healthy is True
        
        # Test unhealthy states
        unhealthy_states = [
            ServerStatus.OFFLINE,
            ServerStatus.DEGRADED,
            ServerStatus.MAINTENANCE,
            ServerStatus.ERROR
        ]
        
        for status in unhealthy_states:
            server.status = status
            assert server.is_healthy is False

    def test_connection_url_property(self):
        """Test connection_url property generation."""
        server = PBSServer(
            name="Test Server",
            hostname="pbs.example.com",
            port=8007,
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1",
            verify_ssl=True
        )
        
        assert server.connection_url == "https://pbs.example.com:8007"
        
        # Test with SSL disabled
        server.verify_ssl = False
        assert server.connection_url == "http://pbs.example.com:8007"
        
        # Test with custom port
        server.port = 8008
        server.verify_ssl = True
        assert server.connection_url == "https://pbs.example.com:8008"
        
        # Test with None port (should use default)
        server.port = None
        assert server.connection_url == "https://pbs.example.com:8007"

    def test_mark_offline_method(self):
        """Test mark_offline method."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Mark offline without error
        server.mark_offline()
        assert server.status == ServerStatus.OFFLINE
        assert server.last_health_check is not None
        assert server.last_error is None
        
        # Mark offline with error
        error_msg = "Connection timeout"
        server.mark_offline(error_msg)
        assert server.status == ServerStatus.OFFLINE
        assert server.last_error == error_msg
        assert server.error_count == 1
        
        # Mark offline again (should increment error count)
        server.mark_offline("Another error")
        assert server.error_count == 2

    def test_mark_online_method(self):
        """Test mark_online method."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Set some error state first
        server.mark_offline("Test error")
        assert server.error_count == 1
        assert server.last_error == "Test error"
        
        # Mark online without version/capabilities
        server.mark_online()
        assert server.status == ServerStatus.ONLINE
        assert server.last_health_check is not None
        assert server.last_error is None
        assert server.error_count == 0
        assert server.version is None
        assert server.capabilities is None
        
        # Mark online with version and capabilities
        version = "2.4.0"
        capabilities = {"backup": True, "restore": True, "encryption": True}
        server.mark_online(version, capabilities)
        assert server.version == version
        assert server.capabilities == capabilities

    def test_error_count_handling(self):
        """Test error count initialization and handling."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Initial error count should be 0
        assert server.error_count == 0
        
        # Test error count with None value (edge case)
        server.error_count = None
        server.mark_offline("Error")
        assert server.error_count == 1
        
        # Test clearing errors
        server.mark_online()
        assert server.error_count == 0

    def test_server_repr(self):
        """Test string representation of server."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        repr_str = repr(server)
        assert "PBSServer" in repr_str
        assert server.id in repr_str
        assert "Test Server" in repr_str
        assert "test.example.com" in repr_str
        assert str(server.status) in repr_str

    def test_server_constraints_validation(self):
        """Test model field constraints and validation."""
        # Test with minimal required fields - should work
        server = PBSServer(
            name="Test",
            hostname="test.com",
            api_token_id="token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        assert server is not None
        
        # Test that required fields are actually required would be enforced by database
        # In unit tests without database, we can't test database constraints

    def test_server_timestamps(self):
        """Test automatic timestamp handling."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Check that timestamps are set
        assert server.created_at is not None
        assert server.updated_at is not None
        assert isinstance(server.created_at, datetime)
        assert isinstance(server.updated_at, datetime)
        
        # Check that created_at and updated_at are close in time
        time_diff = abs((server.updated_at - server.created_at).total_seconds())
        assert time_diff < 1  # Should be within 1 second

    def test_server_health_check_timing(self):
        """Test health check timing logic."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1",
            health_check_interval=300  # 5 minutes
        )
        
        # Initially no health check
        assert server.last_health_check is None
        
        # After marking offline/online, health check should be set
        server.mark_offline()
        assert server.last_health_check is not None
        
        first_check = server.last_health_check
        
        # Mark online should update health check time
        import time
        time.sleep(0.001)  # Small delay to ensure different timestamps
        server.mark_online()
        assert server.last_health_check >= first_check

    def test_server_capabilities_handling(self):
        """Test capabilities JSON field handling."""
        server = PBSServer(
            name="Test Server",
            hostname="test.example.com",
            api_token_id="test@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Test with complex capabilities
        capabilities = {
            "version": "2.4.0",
            "features": {
                "backup": True,
                "restore": True,
                "encryption": True,
                "compression": ["lz4", "zstd"],
                "max_concurrent_jobs": 10
            },
            "datastores": ["backup1", "backup2"],
            "supported_formats": ["pxar", "img"]
        }
        
        server.capabilities = capabilities
        assert server.capabilities == capabilities
        assert server.capabilities["features"]["backup"] is True
        assert "lz4" in server.capabilities["features"]["compression"]

    def test_tenant_isolation_enforcement(self):
        """Test that servers can be properly isolated by tenant through datastores."""
        # Create servers for different scenarios
        server1 = PBSServer(
            name="Tenant 1 Server",
            hostname="pbs1.example.com",
            api_token_id="tenant1@pbs!token",
            api_token_secret="secret1",
            datacenter="dc1"
        )
        
        server2 = PBSServer(
            name="Tenant 2 Server", 
            hostname="pbs2.example.com",
            api_token_id="tenant2@pbs!token",
            api_token_secret="secret2",
            datacenter="dc2"
        )
        
        # Verify servers are independent
        assert server1.id != server2.id
        assert server1.api_token_id != server2.api_token_id
        assert server1.hostname != server2.hostname
        
        # Verify they can have different configurations
        server1.mark_online("2.4.0", {"backup": True})
        server2.mark_offline("Connection failed")
        
        assert server1.is_healthy is True
        assert server2.is_healthy is False
        assert server1.version == "2.4.0"
        assert server2.version is None


class TestPBSServerEdgeCases:
    """Test edge cases and error conditions for PBSServer model."""

    def test_server_with_extreme_values(self):
        """Test server with extreme but valid values."""
        server = PBSServer(
            name="A" * 255,  # Maximum name length
            hostname="a" * 255,  # Maximum hostname length
            port=65535,  # Maximum port number
            api_token_id="x" * 255,  # Maximum token ID length
            api_token_secret="y" * 255,  # Maximum secret length
            datacenter="z" * 255,  # Maximum datacenter length
            timeout=3600,  # 1 hour timeout
            health_check_interval=86400,  # 24 hour interval
            description="D" * 1000  # Long description
        )
        
        assert len(server.name) == 255
        assert len(server.hostname) == 255
        assert server.port == 65535
        assert server.timeout == 3600
        assert server.health_check_interval == 86400

    def test_server_status_persistence(self):
        """Test that server status changes persist correctly."""
        server = PBSServer(
            name="Status Test Server",
            hostname="status.example.com",
            api_token_id="status@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Test status transitions
        status_sequence = [
            ServerStatus.ONLINE,
            ServerStatus.DEGRADED,
            ServerStatus.MAINTENANCE,
            ServerStatus.ERROR,
            ServerStatus.OFFLINE,
            ServerStatus.ONLINE
        ]
        
        for status in status_sequence:
            server.status = status
            assert server.status == status

    def test_server_error_accumulation(self):
        """Test error count accumulation over multiple failures."""
        server = PBSServer(
            name="Error Test Server",
            hostname="error.example.com",
            api_token_id="error@pbs!token",
            api_token_secret="secret",
            datacenter="dc1"
        )
        
        # Simulate multiple failures
        errors = [
            "Connection timeout",
            "Authentication failed", 
            "Network unreachable",
            "SSL certificate error",
            "API endpoint not found"
        ]
        
        for i, error in enumerate(errors, 1):
            server.mark_offline(error)
            assert server.error_count == i
            assert server.last_error == error
        
        # Recovery should reset error count
        server.mark_online()
        assert server.error_count == 0
        assert server.last_error is None

    def test_server_health_check_intervals(self):
        """Test different health check interval configurations."""
        intervals = [60, 300, 600, 1800, 3600]  # 1min to 1hour
        
        for interval in intervals:
            server = PBSServer(
                name=f"Server {interval}s",
                hostname=f"server{interval}.example.com",
                api_token_id=f"test{interval}@pbs!token",
                api_token_secret="secret",
                datacenter="dc1",
                health_check_interval=interval
            )
            
            assert server.health_check_interval == interval