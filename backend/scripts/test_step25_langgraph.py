#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 25 test - LangGraph state machine refactoring
"""
import requests
import time

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_create_project():
    """Test creating a new project"""
    print_section("1. Create Project")

    project_data = {
        "title": "LangGraph测试项目",
        "content": "这是一个测试LangGraph状态机重构的项目。" * 50,  # 500+ chars
        "source_type": "text"
    }

    print(f"Creating project: {project_data['title']}")
    response = requests.post(f"{BASE_URL}/projects", json=project_data)

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Project created: {result['project_id']}")
        return result['project_id']
    else:
        print(f"✗ Failed to create project: {response.text}")
        return None


def test_start_generation(project_id: str):
    """Test starting generation job"""
    print_section("2. Start Generation Job")

    print(f"Starting generation for project {project_id}...")
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/generate")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Job created: {result['job_id']}")
        print(f"  Status: {result['status']}")
        return result['job_id']
    else:
        print(f"✗ Failed to start job: {response.text}")
        return None


def test_poll_job_status(job_id: str, max_wait: int = 120):
    """Poll job status until completion"""
    print_section("3. Poll Job Status")

    print(f"Polling job {job_id} (max {max_wait}s)...")
    start_time = time.time()
    last_stage = None

    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")

        if response.status_code == 200:
            job = response.json()
            status = job['status']
            stage = job.get('stage', 'unknown')
            progress = job.get('progress', 0)

            if stage != last_stage:
                print(f"  Stage: {stage} ({int(progress * 100)}%)")
                last_stage = stage

            if status == 'completed':
                print(f"✓ Job completed!")
                return True
            elif status == 'failed':
                print(f"✗ Job failed: {job.get('error_message', 'Unknown error')}")
                return False

        time.sleep(2)

    print(f"✗ Job did not complete within {max_wait}s")
    return False


def test_verify_result(project_id: str):
    """Verify the result was generated"""
    print_section("4. Verify Result")

    print(f"Checking result for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/result")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Result found")
        print(f"  Video URL: {result.get('video_url', 'N/A')}")
        return True
    else:
        print(f"✗ Failed to get result: {response.text}")
        return False


def test_verify_scenes(project_id: str):
    """Verify scenes were created"""
    print_section("5. Verify Scenes")

    print(f"Checking scenes for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/scenes")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        scenes = response.json()
        print(f"✓ Found {len(scenes)} scenes")
        if scenes:
            print(f"  First scene: {scenes[0]['scene_id']}")
            print(f"  Template: {scenes[0]['template_type']}")
            print(f"  Duration: {scenes[0]['duration_sec']}s")
        return len(scenes) > 0
    else:
        print(f"✗ Failed to get scenes: {response.text}")
        return False


def test_rerender(project_id: str):
    """Test rerender functionality"""
    print_section("6. Test Rerender")

    print(f"Starting rerender for project {project_id}...")
    response = requests.post(f"{BASE_URL}/projects/{project_id}/jobs/rerender")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Rerender job created: {result['job_id']}")

        # Poll rerender job
        job_id = result['job_id']
        print(f"\nPolling rerender job...")
        start_time = time.time()
        last_stage = None

        while time.time() - start_time < 60:
            response = requests.get(f"{BASE_URL}/jobs/{job_id}")

            if response.status_code == 200:
                job = response.json()
                status = job['status']
                stage = job.get('stage', 'unknown')
                progress = job.get('progress', 0)

                if stage != last_stage:
                    print(f"  Stage: {stage} ({int(progress * 100)}%)")
                    last_stage = stage

                if status == 'completed':
                    print(f"✓ Rerender completed!")
                    return True
                elif status == 'failed':
                    print(f"✗ Rerender failed: {job.get('error_message', 'Unknown error')}")
                    return False

            time.sleep(2)

        print(f"✗ Rerender did not complete within 60s")
        return False
    else:
        print(f"✗ Failed to start rerender: {response.text}")
        return False


def main():
    print_section("Step 25 - LangGraph State Machine Test")

    print("\nThis test verifies that the LangGraph refactoring works correctly.")
    print("The pipeline should process jobs using the state machine.")

    # Test 1: Create project
    project_id = test_create_project()
    if not project_id:
        print("\n✗ Test failed: Could not create project")
        return

    # Test 2: Start generation
    job_id = test_start_generation(project_id)
    if not job_id:
        print("\n✗ Test failed: Could not start generation")
        return

    # Test 3: Poll job status
    job_completed = test_poll_job_status(job_id)
    if not job_completed:
        print("\n✗ Test failed: Job did not complete")
        return

    # Test 4: Verify result
    result_ok = test_verify_result(project_id)

    # Test 5: Verify scenes
    scenes_ok = test_verify_scenes(project_id)

    # Test 6: Test rerender
    rerender_ok = test_rerender(project_id)

    print_section("Step 25 Test Summary")

    if project_id:
        print("✓ Project creation works")
    else:
        print("✗ Project creation failed")

    if job_id:
        print("✓ Job creation works")
    else:
        print("✗ Job creation failed")

    if job_completed:
        print("✓ LangGraph pipeline completed successfully")
    else:
        print("✗ LangGraph pipeline failed")

    if result_ok:
        print("✓ Result generation works")
    else:
        print("✗ Result generation failed")

    if scenes_ok:
        print("✓ Scene generation works")
    else:
        print("✗ Scene generation failed")

    if rerender_ok:
        print("✓ Rerender with LangGraph works")
    else:
        print("✗ Rerender failed")

    print("\nLangGraph State Machine:")
    print("  load_project → [parse_article → generate_scenes → validate_scenes]")
    print("              → [load_scenes] → generate_tts → generate_subtitles")
    print("              → prepare_render → END")

    print("\nBenefits of LangGraph refactoring:")
    print("  1. Clear state management")
    print("  2. Explicit node transitions")
    print("  3. Easy to add new stages")
    print("  4. Better error handling")
    print("  5. Conditional routing (generate vs rerender)")

    if all([project_id, job_id, job_completed, result_ok, scenes_ok, rerender_ok]):
        print("\n✅ All tests passed! LangGraph refactoring successful.")
    else:
        print("\n⚠ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
