#!/usr/bin/env python3
"""
Test runner for PBS Server Manager unit tests.

This script runs all unit tests for the PBS server management functionality
and provides a comprehensive validation of the implementation.
"""

import asyncio
import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all PBS server manager tests."""
    print("🧪 Running PBS Server Manager Unit Tests")
    print("=" * 50)
    
    # Change to PCM directory
    pcm_dir = Path(__file__).parent
    
    # Run pytest with specific test file
    test_file = "pcm/tests/services/backup/test_pbs_server_manager.py"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--color=yes",  # Colored output
            "-x",  # Stop on first failure
        ], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All PBS Server Manager tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def validate_test_coverage():
    """Validate that all required test scenarios are covered."""
    print("\n🔍 Validating Test Coverage")
    print("=" * 30)
    
    required_tests = [
        "test_register_server_success",
        "test_register_server_connection_failure", 
        "test_register_server_authentication_failure",
        "test_register_server_validation_failure",
        "test_unregister_server_success",
        "test_unregister_server_not_found",
        "test_perform_health_check_success",
        "test_perform_health_check_failure",
        "test_perform_health_check_server_not_found",
        "test_get_server_statistics",
        "test_list_servers_no_filters",
        "test_list_servers_with_datacenter_filter",
        "test_list_servers_with_status_filter",
        "test_register_server_with_datastores",
        "test_get_server_with_datastores",
        "test_get_server_not_found",
        "test_health_monitoring_task_lifecycle",
        "test_health_monitoring_duplicate_start",
        "test_server_statistics_empty_datastores",
        "test_server_statistics_not_found",
        "test_cleanup",
        "test_register_server_database_error",
        "test_unregister_server_database_error",
        "test_health_check_with_partial_datastore_info",
        "test_update_datastore_info_with_unknown_datastore",
        "test_health_monitoring_task_exception_handling",
        "test_stop_health_monitoring_nonexistent_task",
        "test_register_server_ssl_verification_disabled",
        "test_register_server_custom_port",
        "test_register_server_with_description"
    ]
    
    test_file_path = Path(__file__).parent.parent / "pcm/tests/services/backup/test_pbs_server_manager.py"
    
    if not test_file_path.exists():
        print("❌ Test file not found!")
        return False
    
    test_content = test_file_path.read_text()
    
    missing_tests = []
    for test_name in required_tests:
        if f"def {test_name}" not in test_content:
            missing_tests.append(test_name)
    
    if missing_tests:
        print(f"❌ Missing tests: {missing_tests}")
        return False
    else:
        print(f"✅ All {len(required_tests)} required tests are present")
        return True


def main():
    """Main test runner function."""
    print("🚀 PBS Server Manager Test Suite")
    print("=" * 40)
    
    # Validate test coverage
    coverage_ok = validate_test_coverage()
    
    if not coverage_ok:
        print("\n❌ Test coverage validation failed!")
        return False
    
    # Run the tests
    tests_ok = run_tests()
    
    if tests_ok:
        print("\n🎉 PBS Server Manager unit tests completed successfully!")
        print("\nTest Coverage Summary:")
        print("✅ Server registration and validation")
        print("✅ Health monitoring and status updates") 
        print("✅ Datastore management operations")
        print("✅ Error handling and edge cases")
        print("✅ Database operations and transactions")
        print("✅ Task lifecycle management")
        print("✅ Security and validation features")
        return True
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)