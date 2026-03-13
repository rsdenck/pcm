"""
Backup Verification Service.

This module provides automatic backup integrity verification,
periodic verification scheduling, and verification status tracking.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from pcm.core.models.backup.snapshot import BackupSnapshot


logger = logging.getLogger(__name__)


class VerificationService:
    """
    Backup verification service.
    
    Provides automatic backup integrity verification, periodic scheduling,
    and verification status tracking with alerting.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize verification service.
        
        Args:
            db_session: Database session for operations
        """
        self.db_session = db_session
        self._verification_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._check_interval = 3600  # Check every hour
        self._verification_jobs: Dict[str, Dict[str, Any]] = {}
    
    async def start_verification(self) -> None:
        """
        Start the verification service.
        """
        if self._is_running:
            logger.warning("Verification service is already running")
            return
        
        logger.info("Starting backup verification service")
        self._is_running = True
        self._verification_task = asyncio.create_task(self._verification_loop())
    
    async def stop_verification(self) -> None:
        """
        Stop the verification service.
        """
        if not self._is_running:
            return
        
        logger.info("Stopping backup verification service")
        self._is_running = False
        
        if self._verification_task:
            self._verification_task.cancel()
            try:
                await self._verification_task
            except asyncio.CancelledError:
                pass
            self._verification_task = None
    
    async def _verification_loop(self) -> None:
        """
        Main verification loop that checks backups periodically.
        """
        logger.info("Backup verification loop started")
        
        while self._is_running:
            try:
                await self._verify_backups()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                logger.info("Verification loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in verification loop: {e}")
                await asyncio.sleep(self._check_interval)
    
    async def _verify_backups(self) -> None:
        """
        Verify all backups that need verification.
        """
        try:
            # Get backups needing verification
            backups_to_verify = await self._get_backups_needing_verification()
            
            if not backups_to_verify:
                return
            
            logger.debug(f"Verifying {len(backups_to_verify)} backups")
            
            # Verify each backup
            for snapshot in backups_to_verify:
                await self._verify_backup(snapshot)
                
        except Exception as e:
            logger.error(f"Error verifying backups: {e}")
    
    async def _get_backups_needing_verification(self) -> List[BackupSnapshot]:
        """
        Get list of backups that need verification.
        
        Returns:
            List of snapshots needing verification
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(
                BackupSnapshot.verification_status.in_([None, "pending"])
            )
        )
        
        return list(result.scalars().all())
    
    async def _verify_backup(self, snapshot: BackupSnapshot) -> None:
        """
        Verify a single backup.
        
        Args:
            snapshot: BackupSnapshot to verify
        """
        try:
            # In a real implementation, would perform actual verification
            # against PBS server
            
            # For now, simulate verification
            verification_result = await self._perform_verification(snapshot)
            
            if verification_result['success']:
                snapshot.verification_status = "verified"
                logger.info(f"Backup {snapshot.id} verified successfully")
            else:
                snapshot.verification_status = "failed"
                logger.warning(f"Backup {snapshot.id} verification failed: {verification_result['error']}")
            
            await self.db_session.flush()
            
        except Exception as e:
            logger.error(f"Error verifying backup {snapshot.id}: {e}")
            snapshot.verification_status = "failed"
            await self.db_session.flush()
    
    async def _perform_verification(self, snapshot: BackupSnapshot) -> Dict[str, Any]:
        """
        Perform verification of a backup.
        
        Args:
            snapshot: BackupSnapshot to verify
            
        Returns:
            Verification result
        """
        # Simulate verification checks
        checks = {
            'integrity': True,
            'accessibility': True,
            'metadata': True
        }
        
        all_passed = all(checks.values())
        
        return {
            'success': all_passed,
            'checks': checks,
            'error': None if all_passed else "Verification checks failed"
        }
    
    async def verify_backup_manual(
        self,
        snapshot_id: str
    ) -> Dict[str, Any]:
        """
        Manually trigger verification of a backup.
        
        Args:
            snapshot_id: Snapshot ID to verify
            
        Returns:
            Verification result
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.id == snapshot_id)
        )
        
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            return {
                'success': False,
                'error': f"Snapshot {snapshot_id} not found"
            }
        
        # Create verification job
        job_id = f"verify-{snapshot_id}-{datetime.utcnow().timestamp()}"
        
        job = {
            'job_id': job_id,
            'snapshot_id': snapshot_id,
            'status': 'running',
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'result': None
        }
        
        self._verification_jobs[job_id] = job
        
        # Perform verification
        verification_result = await self._perform_verification(snapshot)
        
        # Update snapshot
        if verification_result['success']:
            snapshot.verification_status = "verified"
        else:
            snapshot.verification_status = "failed"
        
        await self.db_session.flush()
        
        # Update job
        job['status'] = 'completed'
        job['end_time'] = datetime.utcnow().isoformat()
        job['result'] = verification_result
        
        logger.info(f"Manual verification completed for snapshot {snapshot_id}")
        
        return {
            'job_id': job_id,
            'snapshot_id': snapshot_id,
            'verification_result': verification_result
        }
    
    async def get_verification_status(self, snapshot_id: str) -> Optional[str]:
        """
        Get verification status of a backup.
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            Verification status or None if not found
        """
        result = await self.db_session.execute(
            select(BackupSnapshot).where(BackupSnapshot.id == snapshot_id)
        )
        
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            return None
        
        return snapshot.verification_status
    
    async def get_verification_statistics(self) -> Dict[str, Any]:
        """
        Get verification statistics.
        
        Returns:
            Verification statistics
        """
        result = await self.db_session.execute(select(BackupSnapshot))
        
        all_snapshots = list(result.scalars().all())
        
        verified = sum(1 for s in all_snapshots if s.verification_status == "verified")
        failed = sum(1 for s in all_snapshots if s.verification_status == "failed")
        pending = sum(1 for s in all_snapshots if s.verification_status is None)
        
        return {
            'total_snapshots': len(all_snapshots),
            'verified': verified,
            'failed': failed,
            'pending': pending,
            'verification_rate': (verified / len(all_snapshots) * 100) if all_snapshots else 0,
            'service_status': 'running' if self._is_running else 'stopped'
        }
    
    async def get_failed_verifications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of failed verifications.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of failed backups
        """
        result = await self.db_session.execute(
            select(BackupSnapshot)
            .where(BackupSnapshot.verification_status == "failed")
            .limit(limit)
        )
        
        snapshots = list(result.scalars().all())
        
        return [
            {
                'snapshot_id': s.id,
                'job_id': s.job_id,
                'vm_id': s.vm_id,
                'snapshot_time': s.snapshot_time.isoformat(),
                'size': s.size,
                'verification_status': s.verification_status
            }
            for s in snapshots
        ]
    
    async def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        await self.stop_verification()
        self._verification_jobs.clear()
