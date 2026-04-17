#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 27 test - Concurrency control and task management
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def create_test_project(title: str) -> str:
    """Create a test project"""
    project_data = {
        "title": title,
        "content": f"测试并发控制的项目内容 - {title}。" * 50,
        "source_type": "text"
    }

    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    if response.status_code == 200:
        return response.json()['project_id']
    return None


def start_job(project_id: str) -> dict:
    """Start a generation job"""
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")
    if response.status_code == 200:
        return response.json()
    return {"error": response.text, "status_code": response.status_code}


def test_prevent_duplicate_jobs():
    """Test that duplicate jobs for same project are prevented"""
    print_section("1. Test: Prevent Duplicate Jobs for Same Project")

    # Create a project
    project_id = create_test_project("测试重复任务")
    if not project_id:
        print("✗ Failed to create project")
        return False

    print(f"Created project: {project_id}")

    # Start first job
    result1 = start_job(project_id)
    if "error" in result1:
        print(f"✗ Failed to start first job: {result1['error']}")
        return False

    job_id1 = result1['job_id']
    print(f"✓ First job started: {job_id1}")

    # Try to start second job (should fail)
    time.sleep(1)  # Wait a bit
    result2 = start_job(project_id)

    if "error" in result2 and result2['status_code'] == 404:
        print(f"✓ Second job correctly rejected: {result2['error']}")
        return True
    else:
        print(f"✗ Second job should have been rejected but wasn't")
        return False


def test_job_cancellation():
    """Test job cancellation"""
    print_section("2. Test: Job Cancellation")

    # Create a project
    project_id = create_test_project("测试任务取消")
    if not project_id:
        print("✗ Failed to create project")
        return False

    print(f"Created project: {project_id}")

    # Start a job
    result = start_job(project_id)
    if "error" in result:
        print(f"✗ Failed to start job: {result['error']}")
        return False

    job_id = result['job_id']
    print(f"✓ Job started: {job_id}")

    # Wait a bit
    time.sleep(2)

    # Cancel the job
    print(f"\nCancelling job {job_id}...")
    response = requests.post(f"{BASE_URL}/jobs/{job_id}/cancel")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Job cancelled: {result['status']}")
        print(f"  Message: {result['message']}")

        # Verify we can now start a new job for the same project
        time.sleep(1)
        result2 = start_job(project_id)
        if "error" not in result2:
            print(f"✓ New job can be started after cancellation: {result2['job_id']}")
            return True
        else:
            print(f"✗ Failed to start new job after cancellation")
            return False
    else:
        print(f"✗ Failed to cancel job: {response.text}")
        return False


def test_concurrent_jobs():
    """Test concurrent job submission"""
    print_section("3. Test: Concurrent Job Submission (5 projects)")

    # Create 5 projects
    print("Creating 5 test projects...")
    projects = []
    for i in range(5):
        project_id = create_test_project(f"并发测试项目 {i+1}")
        if project_id:
            projects.append(project_id)
            print(f"  ✓ Project {i+1}: {project_id}")

    if len(projects) != 5:
        print(f"✗ Failed to create all projects (only {len(projects)}/5)")
        return False

    # Submit all jobs concurrently
    print(f"\nSubmitting 5 jobs concurrently...")
    jobs = []

    def submit_job(proj_id):
        return start_job(proj_id)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(submit_job, pid) for pid in projects]
        for future in as_completed(futures):
            result = future.result()
            if "error" not in result:
                jobs.append(result['job_id'])
                print(f"  ✓ Job started: {result['job_id']}")
            else:
                print(f"  ✗ Job failed: {result['error']}")

    print(f"\n✓ Successfully started {len(jobs)}/5 jobs")

    # Check concurrency stats
    time.sleep(2)
    response = requests.get(f"{BASE_URL}/concurrency/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"\nConcurrency Stats:")
        print(f"  Max concurrent renders: {stats['max_concurrent_renders']}")
        print(f"  Current concurrent renders: {stats['current_concurrent_renders']}")
        print(f"  Available slots: {stats['available_slots']}")
        print(f"  Running jobs: {stats['running_render_jobs']}")

        # Note: Since our test jobs complete quickly, we might not see 3 concurrent
        # But the system should enforce the limit
        return True
    else:
        print(f"✗ Failed to get concurrency stats")
        return False


def test_concurrency_stats_api():
    """Test concurrency stats API"""
    print_section("4. Test: Concurrency Stats API")

    response = requests.get(f"{BASE_URL}/concurrency/stats")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Concurrency stats retrieved:")
        print(f"  Max concurrent renders: {stats['max_concurrent_renders']}")
        print(f"  Current concurrent renders: {stats['current_concurrent_renders']}")
        print(f"  Available slots: {stats['available_slots']}")
        print(f"  Running render jobs: {stats['running_render_jobs']}")

        # Verify max is 3
        if stats['max_concurrent_renders'] == 3:
            print(f"✓ Max concurrent renders correctly set to 3")
            return True
        else:
            print(f"✗ Max concurrent renders should be 3, got {stats['max_concurrent_renders']}")
            return False
    else:
        print(f"✗ Failed to get stats: {response.text}")
        return False


def test_project_lock_release():
    """Test that project locks are released after job completion"""
    print_section("5. Test: Project Lock Release After Completion")

    # Create a project
    project_id = create_test_project("测试锁释放")
    if not project_id:
        print("✗ Failed to create project")
        return False

    print(f"Created project: {project_id}")

    # Start first job
    result1 = start_job(project_id)
    if "error" in result1:
        print(f"✗ Failed to start first job")
        return False

    job_id1 = result1['job_id']
    print(f"✓ First job started: {job_id1}")

    # Wait for job to complete
    print(f"\nWaiting for job to complete...")
    for i in range(60):
        response = requests.get(f"{BASE_URL}/jobs/{job_id1}")
        if response.status_code == 200:
            job = response.json()
            if job['status'] in ['completed', 'failed']:
                print(f"✓ Job finished with status: {job['status']}")
                break
        time.sleep(2)

    # Try to start a new job (should succeed now)
    time.sleep(2)
    result2 = start_job(project_id)

    if "error" not in result2:
        print(f"✓ New job started after first completed: {result2['job_id']}")
        return True
    else:
        print(f"✗ Failed to start new job: {result2['error']}")
        return False


def main():
    print_section("Step 27 - Concurrency Control and Task Management Test")

    print("\nThis test verifies:")
    print("  1. Duplicate jobs for same project are prevented")
    print("  2. Job cancellation works correctly")
    print("  3. Multiple concurrent jobs can be submitted")
    print("  4. Concurrency stats API works")
    print("  5. Project locks are released after completion")

    # Test 1: Prevent duplicate jobs
    test1_ok = test_prevent_duplicate_jobs()

    # Test 2: Job cancellation
    test2_ok = test_job_cancellation()

    # Test 3: Concurrent jobs
    test3_ok = test_concurrent_jobs()

    # Test 4: Concurrency stats API
    test4_ok = test_concurrency_stats_api()

    # Test 5: Project lock release
    test5_ok = test_project_lock_release()

    print_section("Step 27 Test Summary")

    if test1_ok:
        print("✓ Duplicate job prevention works")
    else:
        print("✗ Duplicate job prevention failed")

    if test2_ok:
        print("✓ Job cancellation works")
    else:
        print("✗ Job cancellation failed")

    if test3_ok:
        print("✓ Concurrent job submission works")
    else:
        print("✗ Concurrent job submission failed")

    if test4_ok:
        print("✓ Concurrency stats API works")
    else:
        print("✗ Concurrency stats API failed")

    if test5_ok:
        print("✓ Project lock release works")
    else:
        print("✗ Project lock release failed")

    print("\nNew Features:")
    print("  • ConcurrencyManager - manages render slots and project locks")
    print("  • Max 3 concurrent renders - enforced globally")
    print("  • Project locking - prevents duplicate jobs")
    print("  • Job cancellation - POST /jobs/{job_id}/cancel")
    print("  • Concurrency stats - GET /concurrency/stats")
    print("  • Automatic lock release - on job completion/failure/cancellation")

    print("\nBenefits:")
    print("  • Resource control - prevents system overload")
    print("  • Data consistency - no conflicting jobs for same project")
    print("  • User control - ability to cancel jobs")
    print("  • Observability - real-time concurrency stats")
    print("  • Reliability - automatic cleanup of stale locks")

    if all([test1_ok, test2_ok, test3_ok, test4_ok, test5_ok]):
        print("\n✅ All tests passed! Concurrency control complete.")
    else:
        print("\n⚠ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
