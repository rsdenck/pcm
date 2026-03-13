"""
Performance Monitoring and Metrics Collection Service.

This module provides performance metrics collection for backup operations,
including OpenTelemetry integration for metrics export.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from pcm.core.models.backup.job import BackupJob, JobStatus
from pcm.core.models.backup.snapshot import BackupSnapshot
from pcm.core.models.backup.pbs_server import PBSServer, ServerStatus


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'tags': self.tags
        }


class PerformanceCollector:
    """
    Performance metrics collection service.
    
    Collects and aggregates performance metrics for backup operations,
    including job execution times, throughput, and resource utilization.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize performance collector.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._metrics: List[PerformanceMetric] = []
        self._collection_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._collection_interval = 30  # Collect metrics every 30 seconds
        self._max_metrics = 10000  # Keep last 10000 metrics in memory
    
    async def start_collection(self) -> None:
        """
        Start the performance metrics collection service.
        """
        if self._is_running:
            logger.warning("Performance collection service is already running")
            return
        
        logger.info("Starting backup performance metrics collection")
        self._is_running = True
        self._collection_task = asyncio.create_task(self._collection_loop())
    
    async def stop_collection(self) -> None:
        """
        Stop the performance metrics collection service.
        """
        if not self._is_running:
            return
        
        logger.info("Stopping backup performance metrics collection")
        self._is_running = False
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            self._collection_task = None
    
    async def _collection_loop(self) -> None:
        """
        Main collection loop that gathers metrics periodically.
        """
        logger.info("Performance collection loop started")
        
        while self._is_running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self._collection_interval)
            except asyncio.CancelledError:
                logger.info("Performance collection loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in performance collection loop: {e}")
                await asyncio.sleep(self._collection_interval)
    
    async def _collect_metrics(self) -> None:
        """
        Collect performance metrics from running jobs and servers.
        """
        try:
            # Collect job performance metrics
            await self._collect_job_metrics()
            
            # Collect server performance metrics
            await self._collect_server_metrics()
            
            # Collect system-wide metrics
            await self._collect_system_metrics()
            
            # Cleanup old metrics if needed
            if len(self._metrics) > self._max_metrics:
                self._metrics = self._metrics[-self._max_metrics:]
                
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    async def _collect_job_metrics(self) -> None:
        """
        Collect performance metrics for backup jobs.
        """
        try:
            # Get running jobs
            result = await self.db_session.execute(
                select(BackupJob).where(
                    BackupJob.status.in_([JobStatus.RUNNING, JobStatus.PENDING])
                )
            )
            
            running_jobs = list(result.scalars().all())
            
            for job in running_jobs:
                # Calculate job duration
                if job.start_time:
                    duration = (datetime.utcnow() - job.start_time).total_seconds()
                    
                    self._add_metric(
                        metric_name="backup_job_duration",
                        value=duration,
                        unit="seconds",
                        tags={
                            'job_id': job.id,
                            'policy_id': job.policy_id,
                            'tenant_id': job.tenant_id,
                            'status': job.status.value
                        }
                    )
                
                # Record job progress
                self._add_metric(
                    metric_name="backup_job_progress",
                    value=job.progress,
                    unit="percent",
                    tags={
                        'job_id': job.id,
                        'policy_id': job.policy_id,
                        'tenant_id': job.tenant_id
                    }
                )
            
            # Get completed jobs from last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            result = await self.db_session.execute(
                select(BackupJob).where(
                    and_(
                        BackupJob.status == JobStatus.COMPLETED,
                        BackupJob.end_time >= one_hour_ago
                    )
                )
            )
            
            completed_jobs = list(result.scalars().all())
            
            for job in completed_jobs:
                if job.start_time and job.end_time:
                    duration = (job.end_time - job.start_time).total_seconds()
                    
                    self._add_metric(
                        metric_name="backup_job_completion_time",
                        value=duration,
                        unit="seconds",
                        tags={
                            'job_id': job.id,
                            'policy_id': job.policy_id,
                            'tenant_id': job.tenant_id
                        }
                    )
                    
                    # Calculate throughput if backup size is available
                    if job.backup_size and duration > 0:
                        throughput = job.backup_size / duration / (1024 * 1024)  # MB/s
                        
                        self._add_metric(
                            metric_name="backup_throughput",
                            value=throughput,
                            unit="MB/s",
                            tags={
                                'job_id': job.id,
                                'policy_id': job.policy_id,
                                'tenant_id': job.tenant_id
                            }
                        )
            
            # Get failed jobs from last hour
            result = await self.db_session.execute(
                select(BackupJob).where(
                    and_(
                        BackupJob.status == JobStatus.FAILED,
                        BackupJob.end_time >= one_hour_ago
                    )
                )
            )
            
            failed_jobs = list(result.scalars().all())
            
            self._add_metric(
                metric_name="backup_job_failures",
                value=len(failed_jobs),
                unit="count",
                tags={'period': 'last_hour'}
            )
            
        except Exception as e:
            logger.error(f"Error collecting job metrics: {e}")
    
    async def _collect_server_metrics(self) -> None:
        """
        Collect performance metrics for PBS servers.
        """
        try:
            # Get all servers
            result = await self.db_session.execute(select(PBSServer))
            servers = list(result.scalars().all())
            
            for server in servers:
                # Record server status
                self._add_metric(
                    metric_name="pbs_server_status",
                    value=1 if server.status == ServerStatus.ONLINE else 0,
                    unit="boolean",
                    tags={
                        'server_id': server.id,
                        'server_name': server.name,
                        'datacenter': server.datacenter
                    }
                )
                
                # Record error count
                if hasattr(server, 'error_count'):
                    self._add_metric(
                        metric_name="pbs_server_errors",
                        value=server.error_count,
                        unit="count",
                        tags={
                            'server_id': server.id,
                            'server_name': server.name
                        }
                    )
            
            # Calculate server availability
            online_servers = sum(1 for s in servers if s.status == ServerStatus.ONLINE)
            total_servers = len(servers)
            
            if total_servers > 0:
                availability = (online_servers / total_servers) * 100
                
                self._add_metric(
                    metric_name="pbs_server_availability",
                    value=availability,
                    unit="percent",
                    tags={'period': 'current'}
                )
            
        except Exception as e:
            logger.error(f"Error collecting server metrics: {e}")
    
    async def _collect_system_metrics(self) -> None:
        """
        Collect system-wide performance metrics.
        """
        try:
            # Get total job counts
            result = await self.db_session.execute(
                select(BackupJob).where(
                    BackupJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING])
                )
            )
            
            active_jobs = len(list(result.scalars().all()))
            
            self._add_metric(
                metric_name="backup_active_jobs",
                value=active_jobs,
                unit="count",
                tags={'period': 'current'}
            )
            
            # Get total snapshot count
            result = await self.db_session.execute(select(BackupSnapshot))
            total_snapshots = len(list(result.scalars().all()))
            
            self._add_metric(
                metric_name="backup_total_snapshots",
                value=total_snapshots,
                unit="count",
                tags={'period': 'cumulative'}
            )
            
            # Calculate average job duration from last 24 hours
            yesterday = datetime.utcnow() - timedelta(hours=24)
            result = await self.db_session.execute(
                select(BackupJob).where(
                    and_(
                        BackupJob.status == JobStatus.COMPLETED,
                        BackupJob.end_time >= yesterday
                    )
                )
            )
            
            completed_jobs = list(result.scalars().all())
            
            if completed_jobs:
                total_duration = sum(
                    (job.end_time - job.start_time).total_seconds()
                    for job in completed_jobs
                    if job.start_time and job.end_time
                )
                avg_duration = total_duration / len(completed_jobs)
                
                self._add_metric(
                    metric_name="backup_average_job_duration",
                    value=avg_duration,
                    unit="seconds",
                    tags={'period': 'last_24h'}
                )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _add_metric(self, metric_name: str, value: float, unit: str, tags: Dict[str, str]) -> None:
        """
        Add a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Metric tags for filtering
        """
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags
        )
        
        self._metrics.append(metric)
    
    def get_metrics(self, metric_name: Optional[str] = None, hours: int = 1) -> List[Dict[str, Any]]:
        """
        Get collected metrics.
        
        Args:
            metric_name: Optional metric name to filter
            hours: Number of hours to look back
            
        Returns:
            List of metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = [
            m for m in self._metrics
            if m.timestamp >= cutoff_time
        ]
        
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        return [m.to_dict() for m in metrics]
    
    def get_metric_summary(self, metric_name: str, hours: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get summary statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            hours: Number of hours to look back
            
        Returns:
            Summary statistics or None if no data
        """
        metrics = self.get_metrics(metric_name, hours)
        
        if not metrics:
            return None
        
        values = [m['value'] for m in metrics]
        
        return {
            'metric_name': metric_name,
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1] if values else None,
            'period_hours': hours
        }
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive performance dashboard data.
        
        Returns:
            Dashboard data with key performance indicators
        """
        # Get job metrics
        job_duration_summary = self.get_metric_summary("backup_job_completion_time", hours=24)
        throughput_summary = self.get_metric_summary("backup_throughput", hours=24)
        
        # Get server metrics
        server_availability = self.get_metric_summary("pbs_server_availability", hours=1)
        
        # Get system metrics
        active_jobs = self.get_metrics("backup_active_jobs", hours=1)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'job_performance': {
                'average_duration': job_duration_summary,
                'throughput': throughput_summary
            },
            'server_performance': {
                'availability': server_availability
            },
            'system_status': {
                'active_jobs': active_jobs[-1]['value'] if active_jobs else 0,
                'collection_status': 'running' if self._is_running else 'stopped'
            }
        }
    
    async def export_metrics_opentelemetry(self) -> Dict[str, Any]:
        """
        Export metrics in OpenTelemetry format.
        
        Returns:
            Metrics in OpenTelemetry format
        """
        return {
            'resourceMetrics': [
                {
                    'resource': {
                        'attributes': [
                            {
                                'key': 'service.name',
                                'value': {'stringValue': 'pcm-backup-module'}
                            }
                        ]
                    },
                    'scopeMetrics': [
                        {
                            'scope': {
                                'name': 'pcm.backup.performance'
                            },
                            'metrics': [
                                {
                                    'name': m['metric_name'],
                                    'unit': m['unit'],
                                    'gauge': {
                                        'dataPoints': [
                                            {
                                                'attributes': m['tags'],
                                                'timeUnixNano': int(
                                                    datetime.fromisoformat(m['timestamp']).timestamp() * 1e9
                                                ),
                                                'asDouble': m['value']
                                            }
                                        ]
                                    }
                                }
                                for m in self.get_metrics(hours=1)
                            ]
                        }
                    ]
                }
            ]
        }
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        await self.stop_collection()
        self._metrics.clear()
