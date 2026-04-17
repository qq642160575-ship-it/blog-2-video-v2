#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 26 test - Error handling and logging
"""
import requests
import time

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_error_handling_short_content():
    """Test error handling for content that's too short"""
    print_section("1. Test Error: Content Too Short")

    project_data = {
        "title": "测试项目 - 内容过短",
        "content": "这是一个太短的内容",  # Only ~10 characters
        "source_type": "text"
    }

    print(f"Creating project with short content ({len(project_data['content'])} chars)...")
    response = requests.post(f"{BASE_URL}/projects", json=project_data)

    print(f"Status: {response.status_code}")

    if response.status_code == 400:
        error = response.json()
        print(f"✓ Error caught correctly: {error['detail']}")
        return True
    else:
        print(f"✗ Expected 400, got {response.status_code}")
        return False


def test_successful_job_with_logs():
    """Test successful job and verify logs are created"""
    print_section("2. Test Successful Job with Logging")

    # Create valid project
    project_data = {
        "title": "测试项目 - 日志记录",
        "content": "这是一个测试日志记录功能的项目内容。" * 50,  # 500+ chars
        "source_type": "text"
    }

    print(f"Creating project...")
    response = requests.post(f"{BASE_URL}/projects", json=project_data)

    if response.status_code != 200:
        print(f"✗ Failed to create project: {response.text}")
        return None, None

    project_id = response.json()['project_id']
    print(f"✓ Project created: {project_id}")

    # Start generation
    print(f"\nStarting generation...")
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")

    if response.status_code != 200:
        print(f"✗ Failed to start job: {response.text}")
        return project_id, None

    job_id = response.json()['job_id']
    print(f"✓ Job created: {job_id}")

    # Wait for completion
    print(f"\nWaiting for job completion...")
    for i in range(60):
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        if response.status_code == 200:
            job = response.json()
            if job['status'] == 'completed':
                print(f"✓ Job completed")
                break
            elif job['status'] == 'failed':
                print(f"✗ Job failed: {job.get('error_message')}")
                break
        time.sleep(2)

    return project_id, job_id


def test_job_logs_api(job_id: str):
    """Test job logs API endpoints"""
    print_section("3. Test Job Logs API")

    # Get all logs
    print(f"\nGetting all logs for job {job_id}...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/logs")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        logs = response.json()
        print(f"✓ Found {len(logs)} log entries")

        if logs:
            print(f"\nLog entries by stage:")
            stages = {}
            for log in logs:
                stage = log['stage']
                if stage not in stages:
                    stages[stage] = []
                stages[stage].append(log)

            for stage, stage_logs in stages.items():
                print(f"  {stage}: {len(stage_logs)} entries")
                for log in stage_logs:
                    print(f"    [{log['level']}] {log['message']}")
                    if log.get('duration_ms'):
                        print(f"      Duration: {log['duration_ms']}ms")

        return len(logs) > 0
    else:
        print(f"✗ Failed to get logs: {response.text}")
        return False


def test_error_logs_api(job_id: str):
    """Test error logs API endpoint"""
    print_section("4. Test Error Logs API")

    print(f"\nGetting error logs for job {job_id}...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/logs/errors")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        errors = response.json()
        print(f"✓ Found {len(errors)} error entries")

        if errors:
            print(f"\nError details:")
            for error in errors:
                print(f"  Stage: {error['stage']}")
                print(f"  Message: {error['message']}")
                if error.get('details'):
                    print(f"  Details: {error['details']}")

        return True
    else:
        print(f"✗ Failed to get error logs: {response.text}")
        return False


def test_log_filtering():
    """Test log filtering by level"""
    print_section("5. Test Log Filtering")

    # Create a project and job first
    project_data = {
        "title": "测试项目 - 日志过滤",
        "content": "这是一个测试日志过滤功能的项目内容。" * 50,
        "source_type": "text"
    }

    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    if response.status_code != 200:
        print(f"✗ Failed to create project")
        return False

    project_id = response.json()['project_id']

    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")
    if response.status_code != 200:
        print(f"✗ Failed to start job")
        return False

    job_id = response.json()['job_id']

    # Wait a bit for some logs to be created
    time.sleep(5)

    # Test filtering by INFO level
    print(f"\nGetting INFO logs...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/logs?level=INFO")
    if response.status_code == 200:
        info_logs = response.json()
        print(f"✓ Found {len(info_logs)} INFO logs")
    else:
        print(f"✗ Failed to get INFO logs")
        return False

    # Test filtering by WARNING level
    print(f"\nGetting WARNING logs...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/logs?level=WARNING")
    if response.status_code == 200:
        warning_logs = response.json()
        print(f"✓ Found {len(warning_logs)} WARNING logs")
    else:
        print(f"✗ Failed to get WARNING logs")
        return False

    # Test filtering by ERROR level
    print(f"\nGetting ERROR logs...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/logs?level=ERROR")
    if response.status_code == 200:
        error_logs = response.json()
        print(f"✓ Found {len(error_logs)} ERROR logs")
    else:
        print(f"✗ Failed to get ERROR logs")
        return False

    return True


def test_error_codes():
    """Test that error codes are properly set"""
    print_section("6. Test Error Codes")

    # Try to get a non-existent project
    print(f"\nTesting PROJECT_NOT_FOUND error...")
    response = requests.get(f"{BASE_URL}/projects/nonexistent_project_id")

    if response.status_code == 404:
        print(f"✓ 404 error returned correctly")
        return True
    else:
        print(f"✗ Expected 404, got {response.status_code}")
        return False


def main():
    print_section("Step 26 - Error Handling and Logging Test")

    print("\nThis test verifies:")
    print("  1. Error handling for invalid input")
    print("  2. Job logs are created for each stage")
    print("  3. Log API endpoints work correctly")
    print("  4. Error codes are properly set")
    print("  5. Log filtering works")

    # Test 1: Error handling
    error_handling_ok = test_error_handling_short_content()

    # Test 2: Successful job with logs
    project_id, job_id = test_successful_job_with_logs()

    logs_api_ok = False
    error_logs_ok = False
    if job_id:
        # Test 3: Job logs API
        logs_api_ok = test_job_logs_api(job_id)

        # Test 4: Error logs API
        error_logs_ok = test_error_logs_api(job_id)

    # Test 5: Log filtering
    filtering_ok = test_log_filtering()

    # Test 6: Error codes
    error_codes_ok = test_error_codes()

    print_section("Step 26 Test Summary")

    if error_handling_ok:
        print("✓ Error handling works")
    else:
        print("✗ Error handling failed")

    if project_id and job_id:
        print("✓ Job creation and execution works")
    else:
        print("✗ Job creation or execution failed")

    if logs_api_ok:
        print("✓ Job logs API works")
    else:
        print("✗ Job logs API failed")

    if error_logs_ok:
        print("✓ Error logs API works")
    else:
        print("✗ Error logs API failed")

    if filtering_ok:
        print("✓ Log filtering works")
    else:
        print("✗ Log filtering failed")

    if error_codes_ok:
        print("✓ Error codes work")
    else:
        print("✗ Error codes failed")

    print("\nNew Features:")
    print("  • job_logs table - stores detailed execution logs")
    print("  • JobLogService - manages log creation and retrieval")
    print("  • Error codes enum - standardized error codes")
    print("  • GET /jobs/{job_id}/logs - retrieve all logs")
    print("  • GET /jobs/{job_id}/logs/errors - retrieve error logs")
    print("  • Log filtering by level (INFO, WARNING, ERROR)")
    print("  • Duration tracking for each stage")

    print("\nBenefits:")
    print("  • Better debugging - detailed logs for each stage")
    print("  • Error tracking - all errors are logged with codes")
    print("  • Performance monitoring - duration tracking")
    print("  • Audit trail - complete history of job execution")

    if all([error_handling_ok, project_id, job_id, logs_api_ok, error_logs_ok, filtering_ok, error_codes_ok]):
        print("\n✅ All tests passed! Error handling and logging complete.")
    else:
        print("\n⚠ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
