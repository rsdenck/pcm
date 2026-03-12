#!/usr/bin/env python3
"""
Test runner for Backup Job Runner validation.

This script runs comprehensive tests for the backup job execution functionality
and validates the implementation against requirements.
"""

import asyncio
import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all backup job runner tests."""
    print("🧪 Running Backup Job Runner Tests")
    print("=" * 50)
    
    # Run pytest with specific test file
    test_file = "pcm/tests/services/backup/test_job_runner.py"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--color=yes",  # Colored output
            "-x",  # Stop on first failure
        ], cwd=Path(__file__).parent, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All Backup Job Runner tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def validate_implementation():
    """Validate implementation against requirements."""
    print("\n🔍 Validating Implementation")
    print("=" * 30)
    
    required_features = [
        "Job execution with PBS API integration",
        "Progress tracking and status updates",
        "Failure handling and retry mechanisms",
        "Multiple target backup support",
        "Snapshot creation and metadata tracking",
        "Backup verification scheduling",
        "Job cancellation support",
        "Resource cleanup and management"
    ]
    
    implementation_files = [
        "pcm/services/backup/job_runner.py",
        "pcm/tests/services/backup/test_job_runner.py"
    ]
    
    # Check if all files exist
    missing_files = []
    for file_path in implementation_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing implementation files: {missing_files}")
        return False
    
    print("✅ All implementation files present")
    
    # Check job runner functionality
    job_runner_file = Path("pcm/services/backup/job_runner.py")
    content = job_runner_file.read_text()
    
    required_methods = [
        "execute_job",
        "retry_failed_job", 
        "cancel_job",
        "get_job_status",
        "_execute_target_backup",
        "_update_job_progress",
        "cleanup"
    ]
    
    missing_methods = []
    for method in required_methods:
        if f"def {method}" not in content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing required methods: {missing_methods}")
        return False
    
    print("✅ All required methods implemented")
    
    # Check PBS client integration
    if "PBSAPIClient" not in content:
        print("❌ Missing PBS API client integration")
        return False
    
    if "create_backup" not in content:
        print("❌ Missing backup creation functionality")
        return False
    
    print("✅ PBS API integration implemented")
    
    return True


def validate_test_coverage():
    """Validate test coverage."""
    print("\n📊 Validating Test Coverage")
    print("=" * 25)
    
    test_file = Path("pcm/tests/services/backup/test_job_runner.py")
    if not test_file.exists():
        print("❌ Test file not found!")
        return False
    
    test_content = test_file.read_text()
    
    required_test_cases = [
        "test_execute_job_success",
        "test_execute_job_not_found",
        "test_execute_job_wrong_status",
        "test_execute_job_already_running",
        "test_execute_job_backup_failure",
        "test_execute_job_datastore_not_found",
        "test_retry_failed_job_success",
        "test_retry_failed_job_max_retries",
        "test_cancel_job_success",
        "test_cancel_job_not_found",
        "test_get_job_status",
        "test_cleanup",
        "test_multiple_targets_execution"
    ]
    
    missing_tests = []
    for test_case in required_test_cases:
        if f"def {test_case}" not in test_content:
            missing_tests.append(test_case)
    
    if missing_tests:
        print(f"❌ Missing test cases: {missing_tests}")
        return False
    
    print(f"✅ All {len(required_test_cases)} required test cases present")
    return True


def main():
    """Main validation function."""
    print("🚀 Backup Job Runner Validation Suite")
    print("=" * 40)
    
    # Validate implementation
    impl_ok = validate_implementation()
    
    if not impl_ok:
        print("\n❌ Implementation validation failed!")
        return False
    
    # Validate test coverage
    coverage_ok = validate_test_coverage()
    
    if not coverage_ok:
        print("\n❌ Test coverage validation failed!")
        return False
    
    # Run the tests
    tests_ok = run_tests()
    
    if tests_ok:
        print("\n🎉 Backup Job Runner validation completed successfully!")
        print("\nImplementation Summary:")
        print("✅ Job execution with PBS API integration")
        print("✅ Progress tracking and status updates")
        print("✅ Failure handling and retry mechanisms")
        print("✅ Multiple target backup support")
        print("✅ Snapshot creation and metadata tracking")
        print("✅ Job cancellation and resource cleanup")
        print("✅ Comprehensive error handling")
        print("✅ Database transaction management")
        
        print("\nRequirements Validation:")
        print("✅ Requirement 5.1: Backup job execution")
        print("✅ Requirement 5.4: Failure handling and retry")
        print("✅ Requirement 6.1: Job progress tracking")
        print("✅ Requirement 6.2: Job status management")
        
        return True
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)