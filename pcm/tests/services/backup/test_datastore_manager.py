"""
Tests for DatastoreManager service.

Tests datastore provisioning, capacity monitoring, threshold alerting,
and tenant-based assignment functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from pcm.core.models.backup.datastore import Datastore, DatastoreStatus
from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus
from pcm.services.backup.datastore_manager import (
    DatastoreManager,
    DatastoreManagerError,
    DatastoreProvisioningError,
    DatastoreCapacityError
)
from pcm.services.backup.pbs_client import PBSClientError


class TestDatastoreManager:
    """Test cases for DatastoreManager class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def datastore_manager(self, mock_db_session):
        """Create DatastoreManager instance."""
        return DatastoreManager(mock_db_session)
    
    @pytest.fixture
    def mock_pbs_server(self):
        """Create mock PBS server."""
        server = MagicMock(spec=PBSServer)
        server.id = "server-123"
        server.name = "test-pbs"
        server.status = ServerStatus.ONLINE
        return server
    
    @pytest.fixture
    def mock_datastore(self):
        """Create mock datastore."""
        datastore = MagicMock(spec=Datastore)
        datastore.id = "ds-123"
        datastore.name = "test-datastore"
        datastore.tenant_id = "tenant-123"
        datastore.pbs_server_id = "server-123"
        datastore.status = DatastoreStatus.ACTIVE
        datastore.total_capacity = 1000000
        datastore.used_capacity = 500000
        datastore.available_capacity = 500000
        datastore.warning_threshold = 80
        datastore.critical_threshold = 90
        datastore.capacity_check_interval = 3600
        datastore.last_capacity_check = datetime.utcnow()
        datastore.usage_percentage = 50.0
        datastore.is_over_warning_threshold = False
        datastore.is_over_critical_threshold = False
        datastore.is_healthy = True
        return datastore
    
    @pytest.mark.asyncio
    async def test_provision_datastore_success(self, datastore_manager, mock_db_session, mock_pbs_server):
        """Test successful datastore provisioning."""
        # Mock database queries
        mock_result1 = AsyncMock()
        mock_result1.scalar_one_or_none = MagicMock(return_value=mock_pbs_server)
        mock_result2 = AsyncMock()
        mock_result2.scalar_one_or_none = MagicMock(return_value=None)
        
        mock_db_session.execute.side_effect = [mock_result1, mock_result2]
        
        # Mock PBS client
        mock_client = AsyncMock()
        mock_client.create_datastore = AsyncMock()
        
        with patch('pcm.services.backup.datastore_manager.PBSAPIClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with patch.object(datastore_manager, '_start_datastore_monitoring') as mock_monitoring:
                result = await datastore_manager.provision_datastore(
                    pbs_server_id="server-123",
                    tenant_id="tenant-123",
                    name="test-datastore",
                    path="/backup/test",
                    description="Test datastore",
                    compress=True
                )
        
        # Verify PBS client was called
        mock_client.create_datastore.assert_called_once_with(
            "test-datastore", "/backup/test", compress=True
        )
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        
        # Verify monitoring was started
        mock_monitoring.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_provision_datastore_server_not_found(self, datastore_manager, mock_db_session):
        """Test datastore provisioning with non-existent server."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(DatastoreProvisioningError, match="PBS server .* not found"):
            await datastore_manager.provision_datastore(
                pbs_server_id="nonexistent",
                tenant_id="tenant-123",
                name="test-datastore",
                path="/backup/test"
            )
    
    @pytest.mark.asyncio
    async def test_provision_datastore_server_offline(self, datastore_manager, mock_db_session, mock_pbs_server):
        """Test datastore provisioning with offline server."""
        mock_pbs_server.status = ServerStatus.OFFLINE
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_pbs_server)
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(DatastoreProvisioningError, match="is not online"):
            await datastore_manager.provision_datastore(
                pbs_server_id="server-123",
                tenant_id="tenant-123",
                name="test-datastore",
                path="/backup/test"
            )
    
    @pytest.mark.asyncio
    async def test_provision_datastore_already_exists(self, datastore_manager, mock_db_session, mock_pbs_server, mock_datastore):
        """Test datastore provisioning with existing name."""
        mock_result1 = AsyncMock()
        mock_result1.scalar_one_or_none = MagicMock(return_value=mock_pbs_server)
        mock_result2 = AsyncMock()
        mock_result2.scalar_one_or_none = MagicMock(return_value=mock_datastore)
        
        mock_db_session.execute.side_effect = [mock_result1, mock_result2]
        
        with pytest.raises(DatastoreProvisioningError, match="already exists"):
            await datastore_manager.provision_datastore(
                pbs_server_id="server-123",
                tenant_id="tenant-123",
                name="test-datastore",
                path="/backup/test"
            )
    
    @pytest.mark.asyncio
    async def test_assign_datastore_to_tenant_success(self, datastore_manager, mock_db_session, mock_datastore):
        """Test successful datastore tenant assignment."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_datastore)
        mock_db_session.execute.return_value = mock_result
        
        result = await datastore_manager.assign_datastore_to_tenant("ds-123", "new-tenant")
        
        assert mock_datastore.tenant_id == "new-tenant"
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_datastore)
    
    @pytest.mark.asyncio
    async def test_assign_datastore_to_tenant_not_found(self, datastore_manager, mock_db_session):
        """Test datastore tenant assignment with non-existent datastore."""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(DatastoreManagerError, match="not found"):
            await datastore_manager.assign_datastore_to_tenant("nonexistent", "tenant-123")
    
    @pytest.mark.asyncio
    async def test_get_tenant_datastores(self, datastore_manager, mock_db_session):
        """Test getting tenant datastores."""
        mock_datastores = [MagicMock(spec=Datastore) for _ in range(3)]
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_datastores
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result
        
        result = await datastore_manager.get_tenant_datastores("tenant-123")
        
        assert len(result) == 3
        assert result == mock_datastores
    
    @pytest.mark.asyncio
    async def test_get_tenant_datastores_with_status_filter(self, datastore_manager, mock_db_session):
        """Test getting tenant datastores with status filter."""
        mock_datastores = [MagicMock(spec=Datastore)]
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_datastores
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result
        
        result = await datastore_manager.get_tenant_datastores(
            "tenant-123", 
            status_filter=DatastoreStatus.ACTIVE
        )
        
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_update_datastore_capacity_success(self, datastore_manager, mock_db_session, mock_datastore):
        """Test successful datastore capacity update."""
        # Mock datastore with PBS server
        mock_pbs_server = MagicMock(spec=PBSServer)
        mock_datastore.pbs_server = mock_pbs_server
        mock_datastore.last_capacity_check = datetime.utcnow() - timedelta(hours=2)
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_datastore)
        mock_db_session.execute.return_value = mock_result
        
        # Mock PBS client
        mock_client = AsyncMock()
        mock_client.get_datastore_status.return_value = {
            'total': 2000000,
            'used': 1000000,
            'avail': 1000000
        }
        
        with patch('pcm.services.backup.datastore_manager.PBSAPIClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with patch.object(datastore_manager, '_check_capacity_thresholds') as mock_check:
                result = await datastore_manager.update_datastore_capacity("ds-123", force_update=True)
        
        # Verify capacity update was called
        mock_datastore.update_capacity.assert_called_once_with(2000000, 1000000, 1000000)
        mock_db_session.commit.assert_called_once()
        mock_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_datastore_capacity_skip_recent_check(self, datastore_manager, mock_db_session, mock_datastore):
        """Test skipping capacity update for recently checked datastore."""
        mock_datastore.last_capacity_check = datetime.utcnow() - timedelta(minutes=30)
        mock_datastore.capacity_check_interval = 3600  # 1 hour
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_datastore)
        mock_db_session.execute.return_value = mock_result
        
        result = await datastore_manager.update_datastore_capacity("ds-123", force_update=False)
        
        # Should return without updating
        assert result == mock_datastore
        mock_datastore.update_capacity.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_datastore_capacity_pbs_error(self, datastore_manager, mock_db_session, mock_datastore):
        """Test capacity update with PBS client error."""
        mock_pbs_server = MagicMock(spec=PBSServer)
        mock_datastore.pbs_server = mock_pbs_server
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_datastore)
        mock_db_session.execute.return_value = mock_result
        
        # Mock PBS client error
        mock_client = AsyncMock()
        mock_client.get_datastore_status.side_effect = PBSClientError("Connection failed")
        
        with patch('pcm.services.backup.datastore_manager.PBSAPIClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(DatastoreManagerError, match="Failed to update datastore capacity"):
                await datastore_manager.update_datastore_capacity("ds-123", force_update=True)
        
        # Verify error was marked
        mock_datastore.mark_error.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_monitor_all_datastores(self, datastore_manager, mock_db_session):
        """Test monitoring all datastores."""
        # Create mock datastores
        mock_datastores = []
        for i in range(3):
            ds = MagicMock(spec=Datastore)
            ds.id = f"ds-{i}"
            ds.name = f"datastore-{i}"
            ds.tenant_id = f"tenant-{i}"
            ds.status = DatastoreStatus.ACTIVE
            ds.usage_percentage = 50.0 + i * 10
            ds.is_healthy = True
            ds.is_over_warning_threshold = i >= 2
            ds.is_over_critical_threshold = False
            mock_datastores.append(ds)
        
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_datastores
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result
        
        # Mock update_datastore_capacity to return updated datastores
        async def mock_update(ds_id):
            return next(ds for ds in mock_datastores if ds.id == ds_id)
        
        with patch.object(datastore_manager, 'update_datastore_capacity', side_effect=mock_update):
            result = await datastore_manager.monitor_all_datastores()
        
        assert result['total_datastores'] == 3
        assert result['updated'] == 3
        assert result['errors'] == 0
        assert result['warnings'] == 1  # datastore-2 is over warning threshold
        assert result['critical'] == 0
        assert len(result['details']) == 3
    
    @pytest.mark.asyncio
    async def test_get_datastore_statistics(self, datastore_manager, mock_db_session):
        """Test getting datastore statistics."""
        # Create mock datastores with different statuses and capacities
        mock_datastores = []
        
        # Active datastore
        ds1 = MagicMock(spec=Datastore)
        ds1.status = DatastoreStatus.ACTIVE
        ds1.total_capacity = 1000000
        ds1.used_capacity = 500000
        ds1.is_over_warning_threshold = False
        ds1.is_over_critical_threshold = False
        ds1.last_backup = datetime.utcnow() - timedelta(hours=2)
        mock_datastores.append(ds1)
        
        # Full datastore
        ds2 = MagicMock(spec=Datastore)
        ds2.status = DatastoreStatus.FULL
        ds2.total_capacity = 2000000
        ds2.used_capacity = 1800000
        ds2.is_over_warning_threshold = True
        ds2.is_over_critical_threshold = True
        ds2.last_backup = datetime.utcnow() - timedelta(days=2)
        mock_datastores.append(ds2)
        
        # Inactive datastore
        ds3 = MagicMock(spec=Datastore)
        ds3.status = DatastoreStatus.INACTIVE
        ds3.total_capacity = 500000
        ds3.used_capacity = 100000
        ds3.is_over_warning_threshold = False
        ds3.is_over_critical_threshold = False
        ds3.last_backup = None
        mock_datastores.append(ds3)
        
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_datastores
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result
        
        result = await datastore_manager.get_datastore_statistics()
        
        assert result['total_datastores'] == 3
        assert result['active_datastores'] == 1
        assert result['total_capacity'] == 3500000
        assert result['used_capacity'] == 2400000
        assert result['available_capacity'] == 1100000
        assert result['usage_percentage'] == pytest.approx(68.57, rel=1e-2)
        assert result['status_breakdown']['active'] == 1
        assert result['status_breakdown']['full'] == 1
        assert result['status_breakdown']['inactive'] == 1
        assert result['threshold_violations']['warning'] == 1
        assert result['threshold_violations']['critical'] == 1
        assert result['recent_activity']['datastores_with_recent_backups'] == 1
    
    @pytest.mark.asyncio
    async def test_get_datastore_statistics_with_tenant_filter(self, datastore_manager, mock_db_session):
        """Test getting datastore statistics with tenant filter."""
        mock_datastore = MagicMock(spec=Datastore)
        mock_datastore.last_backup = None
        mock_datastore.status = DatastoreStatus.ACTIVE
        mock_datastore.total_capacity = 1000000
        mock_datastore.used_capacity = 500000
        mock_datastore.is_over_warning_threshold = False
        mock_datastore.is_over_critical_threshold = False
        mock_datastores = [mock_datastore]
        mock_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_datastores
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute.return_value = mock_result
        
        result = await datastore_manager.get_datastore_statistics(tenant_id="tenant-123")
        
        assert result['tenant_id'] == "tenant-123"
    
    @pytest.mark.asyncio
    async def test_check_capacity_thresholds_critical_alert(self, datastore_manager, mock_datastore):
        """Test capacity threshold checking with critical alert."""
        mock_datastore.usage_percentage = 95.0
        mock_datastore.is_over_critical_threshold = True
        mock_datastore.is_over_warning_threshold = True
        mock_datastore.critical_threshold = 90
        
        with patch.object(datastore_manager, '_trigger_alert') as mock_alert:
            await datastore_manager._check_capacity_thresholds(
                mock_datastore, 
                DatastoreStatus.ACTIVE
            )
        
        mock_alert.assert_called_once()
        alert_data = mock_alert.call_args[0][0]
        assert alert_data['alert_type'] == 'critical'
        assert alert_data['threshold'] == 90
        assert 'exceeded critical threshold' in alert_data['message']
    
    @pytest.mark.asyncio
    async def test_check_capacity_thresholds_warning_alert(self, datastore_manager, mock_datastore):
        """Test capacity threshold checking with warning alert."""
        mock_datastore.usage_percentage = 85.0
        mock_datastore.is_over_critical_threshold = False
        mock_datastore.is_over_warning_threshold = True
        mock_datastore.warning_threshold = 80
        
        with patch.object(datastore_manager, '_trigger_alert') as mock_alert:
            await datastore_manager._check_capacity_thresholds(
                mock_datastore, 
                DatastoreStatus.ACTIVE
            )
        
        mock_alert.assert_called_once()
        alert_data = mock_alert.call_args[0][0]
        assert alert_data['alert_type'] == 'warning'
        assert alert_data['threshold'] == 80
        assert 'exceeded warning threshold' in alert_data['message']
    
    @pytest.mark.asyncio
    async def test_check_capacity_thresholds_recovery_alert(self, datastore_manager, mock_datastore):
        """Test capacity threshold checking with recovery alert."""
        mock_datastore.usage_percentage = 70.0
        mock_datastore.is_over_critical_threshold = False
        mock_datastore.is_over_warning_threshold = False
        
        with patch.object(datastore_manager, '_trigger_alert') as mock_alert:
            await datastore_manager._check_capacity_thresholds(
                mock_datastore, 
                DatastoreStatus.FULL  # Previously full
            )
        
        mock_alert.assert_called_once()
        alert_data = mock_alert.call_args[0][0]
        assert alert_data['alert_type'] == 'recovery'
        assert 'recovered from capacity issues' in alert_data['message']
    
    @pytest.mark.asyncio
    async def test_trigger_alert(self, datastore_manager):
        """Test alert triggering with callbacks."""
        alert_data = {
            'alert_type': 'critical',
            'message': 'Test alert',
            'datastore_name': 'test-ds'
        }
        
        # Register sync and async callbacks
        sync_callback = MagicMock()
        async_callback = AsyncMock()
        
        datastore_manager.register_alert_callback(sync_callback)
        datastore_manager.register_alert_callback(async_callback)
        
        await datastore_manager._trigger_alert(alert_data)
        
        sync_callback.assert_called_once_with(alert_data)
        async_callback.assert_called_once_with(alert_data)
    
    def test_register_unregister_alert_callback(self, datastore_manager):
        """Test registering and unregistering alert callbacks."""
        callback = MagicMock()
        
        # Register callback
        datastore_manager.register_alert_callback(callback)
        assert callback in datastore_manager._alert_callbacks
        
        # Unregister callback
        datastore_manager.unregister_alert_callback(callback)
        assert callback not in datastore_manager._alert_callbacks
    
    @pytest.mark.asyncio
    async def test_start_datastore_monitoring(self, datastore_manager, mock_db_session, mock_datastore):
        """Test starting datastore monitoring."""
        datastore_id = "ds-123"
        
        # Mock the monitoring loop to avoid infinite loop
        with patch.object(datastore_manager, 'update_datastore_capacity') as mock_update:
            mock_update.return_value = mock_datastore
            mock_datastore.status = DatastoreStatus.INACTIVE  # Will break the loop
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_datastore
            
            await datastore_manager._start_datastore_monitoring(datastore_id)
            
            # Give the task a moment to start
            await asyncio.sleep(0.1)
            
            assert datastore_id in datastore_manager._monitoring_tasks
            
            # Clean up
            await datastore_manager._stop_datastore_monitoring(datastore_id)
    
    @pytest.mark.asyncio
    async def test_stop_datastore_monitoring(self, datastore_manager):
        """Test stopping datastore monitoring."""
        datastore_id = "ds-123"
        
        # Create a mock task that can be awaited
        async def mock_task():
            pass
        
        task = asyncio.create_task(mock_task())
        task.cancel = MagicMock()
        datastore_manager._monitoring_tasks[datastore_id] = task
        
        await datastore_manager._stop_datastore_monitoring(datastore_id)
        
        task.cancel.assert_called_once()
        assert datastore_id not in datastore_manager._monitoring_tasks
    
    @pytest.mark.asyncio
    async def test_start_monitoring_all_datastores(self, datastore_manager, mock_db_session):
        """Test starting monitoring for all datastores."""
        # Mock datastore IDs
        mock_result = AsyncMock()
        mock_result.fetchall = MagicMock(return_value=[("ds-1",), ("ds-2",), ("ds-3",)])
        mock_db_session.execute.return_value = mock_result
        
        with patch.object(datastore_manager, '_start_datastore_monitoring') as mock_start:
            await datastore_manager.start_monitoring_all_datastores()
        
        assert mock_start.call_count == 3
        mock_start.assert_any_call("ds-1")
        mock_start.assert_any_call("ds-2")
        mock_start.assert_any_call("ds-3")
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_all_datastores(self, datastore_manager):
        """Test stopping monitoring for all datastores."""
        # Add some mock monitoring tasks
        datastore_manager._monitoring_tasks = {
            "ds-1": AsyncMock(),
            "ds-2": AsyncMock(),
            "ds-3": AsyncMock()
        }
        
        with patch.object(datastore_manager, '_stop_datastore_monitoring') as mock_stop:
            await datastore_manager.stop_monitoring_all_datastores()
        
        assert mock_stop.call_count == 3
        mock_stop.assert_any_call("ds-1")
        mock_stop.assert_any_call("ds-2")
        mock_stop.assert_any_call("ds-3")
    
    @pytest.mark.asyncio
    async def test_cleanup(self, datastore_manager):
        """Test cleanup method."""
        # Add some callbacks and monitoring tasks
        datastore_manager._alert_callbacks = [MagicMock(), MagicMock()]
        datastore_manager._monitoring_tasks = {"ds-1": AsyncMock()}
        
        with patch.object(datastore_manager, 'stop_monitoring_all_datastores') as mock_stop:
            await datastore_manager.cleanup()
        
        mock_stop.assert_called_once()
        assert len(datastore_manager._alert_callbacks) == 0


class TestDatastoreManagerIntegration:
    """Integration tests for DatastoreManager."""
    
    @pytest.mark.asyncio
    async def test_full_datastore_lifecycle(self):
        """Test complete datastore lifecycle from provisioning to monitoring."""
        # This would be an integration test that requires actual database
        # and potentially PBS server setup. For now, we'll skip it.
        pytest.skip("Integration test requires full environment setup")
    
    @pytest.mark.asyncio
    async def test_capacity_monitoring_with_alerts(self):
        """Test capacity monitoring with threshold alerts."""
        # This would test the full monitoring loop with real alerts
        pytest.skip("Integration test requires full environment setup")