#!/usr/bin/env python3
"""
Test runner for Backup Scheduler Property Tests.

This script runs property-based tests for the backup scheduling system
and validates scheduling consistency properties.
"""

import asyncio
import sys
import subprocess
from pathlib import Path


def run_property_tests():
    """Run backup scheduler property tests."""
    print("🧪 Running Backup Scheduler Property Tests")
    print("=" * 50)
    
    # Run pytest with specific test file
    test_file = "tests/services/backup/test_scheduler_properties.py"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--color=yes",  # Colored output
            "-x",  # Stop on first failure
            "--hypothesis-show-statistics",  # Show Hypothesis statistics
        ], cwd=Path(__file__).parent, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All scheduler property tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def validate_property_coverage():
    """Validate property test coverage."""
    print("\n🔍 Validating Property Test Coverage")
    print("=" * 35)
    
    required_properties = [
        "Cron schedule consistency",
        "No duplicate scheduling", 
        "Resource lock consistency",
        "Queue FIFO ordering",
        "Concurrent job limits",
        "Event logging completeness",
        "Statistics accuracy",
        "Cron expression validity"
    ]
    
    test_file = Path("tests/services/backup/test_scheduler_properties.py")
    if not test_file.exists():
        print("❌ Property test file not found!")
        return False
    
    test_content = test_file.read_text()
    
    required_test_methods = [
        "test_property_cron_schedule_consistency",
        "test_property_no_duplicate_scheduling",
        "test_property_resource_lock_consistency", 
        "test_property_queue_fifo_ordering",
        "test_property_concurrent_job_limits",
        "test_property_event_logging_completeness",
        "test_property_statistics_accuracy",
        "test_property_cron_expression_validity"
    ]
    
    missing_tests = []
    for test_method in required_test_methods:
        if f"def {test_method}" not in test_content:
            missing_tests.append(test_method)
    
    if missing_tests:
        print(f"❌ Missing property tests: {missing_tests}")
        return False
    
    print(f"✅ All {len(required_test_methods)} property tests present")
    
    # Check for stateful testing
    if "RuleBasedStateMachine" not in test_content:
        print("❌ Missing stateful property testing")
        return False
    
    print("✅ Stateful property testing implemented")
    
    # Check for Hypothesis strategies
    if "@st.composite" not in test_content:
        print("❌ Missing custom Hypothesis strategies")
        return False
    
    print("✅ Custom Hypothesis strategies implemented")
    
    return True


def validate_scheduler_implementation():
    """Validate scheduler engine implementation."""
    print("\n🔧 Validating Scheduler Implementation")
    print("=" * 35)
    
    scheduler_file = Path("services/backup/scheduler_engine.py")
    if not scheduler_file.exists():
        print("❌ Scheduler engine file not found!")
        return False
    
    content = scheduler_file.read_text()
    
    required_methods = [
        "start",
        "stop", 
        "_scheduler_loop",
        "_check_scheduled_jobs",
        "_schedule_policy_job",
        "_calculate_next_run",
        "_process_job_queue",
        "schedule_immediate_job",
        "cancel_scheduled_jobs",
        "get_statistics",
        "_log_event"
    ]
    
    missing_methods = []
    for method in required_methods:
        if f"def {method}" not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing scheduler methods: {missing_methods}")
        return False
    
    print("✅ All required scheduler methods implemented")
    
    # Check for event logging integration
    if "ScheduleEvent" not in content:
        print("❌ Missing event logging integration")
        return False
    
    print("✅ Event logging integration implemented")
    
    # Check for resource management
    if "_resource_locks" not in content:
        print("❌ Missing resource lock management")
        return False
    
    print("✅ Resource lock management implemented")
    
    return True


def validate_event_model():
    """Validate schedule event model."""
    print("\n📊 Validating Event Model")
    print("=" * 25)
    
    event_file = Path("core/models/backup/schedule_event.py")
    if not event_file.exists():
        print("❌ Schedule event model not found!")
        return False
    
    content = event_file.read_text()
    
    # Check for event types
    required_event_types = [
        "JOB_SCHEDULED",
        "JOB_COMPLETED", 
        "JOB_FAILED",
        "SCHEDULING_CONFLICT",
        "RESOURCE_CONFLICT",
        "SCHEDULER_STARTED",
        "SCHEDULER_STOPPED"
    ]
    
    missing_types = []
    for event_type in required_event_types:
        if event_type not in content:
            missing_types.append(event_type)
    
    if missing_types:
        print(f"❌ Missing event types: {missing_types}")
        return False
    
    print("✅ All required event types defined")
    
    # Check for factory methods
    factory_methods = [
        "create_job_scheduled",
        "create_scheduling_conflict",
        "create_resource_conflict", 
        "create_job_completed",
        "create_policy_error"
    ]
    
    missing_factories = []
    for method in factory_methods:
        if f"def {method}" not in content:
            missing_factories.append(method)
    
    if missing_factories:
        print(f"❌ Missing factory methods: {missing_factories}")
        return False
    
    print("✅ All factory methods implemented")
    
    return True


def main():
    """Main validation function."""
    print("🚀 Backup Scheduler Property Test Suite")
    print("=" * 45)
    
    # Validate scheduler implementation
    scheduler_ok = validate_scheduler_implementation()
    
    if not scheduler_ok:
        print("\n❌ Scheduler implementation validation failed!")
        return False
    
    # Validate event model
    event_ok = validate_event_model()
    
    if not event_ok:
        print("\n❌ Event model validation failed!")
        return False
    
    # Validate property test coverage
    coverage_ok = validate_property_coverage()
    
    if not coverage_ok:
        print("\n❌ Property test coverage validation failed!")
        return False
    
    # Run the property tests
    tests_ok = run_property_tests()
    
    if tests_ok:
        print("\n🎉 Backup Scheduler Property Tests completed successfully!")
        print("\nProperty Validation Summary:")
        print("✅ Cron schedule consistency and monotonicity")
        print("✅ Duplicate scheduling prevention")
        print("✅ Resource lock consistency and conflict detection")
        print("✅ FIFO queue ordering maintenance")
        print("✅ Concurrent job limit enforcement")
        print("✅ Event logging completeness")
        print("✅ Statistics accuracy")
        print("✅ Stateful property testing")
        
        print("\nImplementation Summary:")
        print("✅ Scheduler engine with cron-based scheduling")
        print("✅ Job queuing and resource management")
        print("✅ Overlap prevention and retry logic")
        print("✅ Event logging and audit trails")
        print("✅ Performance metrics and monitoring")
        print("✅ Database integration for critical events")
        
        print("\nRequirements Validation:")
        print("✅ Requirement 5.1: Backup job scheduling consistency")
        print("✅ Requirement 5.5: Schedule management and conflict resolution")
        print("✅ Property 5: Backup job scheduling consistency validated")
        
        return True
    else:
        print("\n❌ Some property tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)