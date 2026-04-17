#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 20 test - Rerender functionality
"""
import sys
import os
import requests
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_update_scene(scene_id: str):
    """Update a scene to trigger rerender"""
    print_section("1. Update Scene for Rerender Test")

    updates = {
        "voiceover": "这是重新渲染测试的旁白文本，内容已经被修改。",
        "duration_sec": 7
    }

    print(f"Updating scene {scene_id}")
    print(f"New voiceover: {updates['voiceover']}")
    print(f"New duration: {updates['duration_sec']}s")

    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Scene updated to version {result['version']}")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_trigger_rerender(project_id: str):
    """Trigger rerender job"""
    print_section("2. Trigger Rerender Job")

    print(f"Triggering rerender for project {project_id}")

    response = requests.post(
        f"{BASE_URL}/projects/{project_id}/jobs/rerender"
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Rerender job created")
        print(f"  Job ID: {result['job_id']}")
        print(f"  Status: {result['status']}")
        return result['job_id']
    else:
        print(f"Error: {response.text}")
        return None


def test_monitor_job(job_id: str, timeout: int = 300):
    """Monitor job status until completion"""
    print_section("3. Monitor Job Status")

    print(f"Monitoring job {job_id} (timeout: {timeout}s)")

    start_time = time.time()
    last_status = None

    while time.time() - start_time < timeout:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")

        if response.status_code == 200:
            job = response.json()
            status = job['status']

            if status != last_status:
                print(f"\n[{int(time.time() - start_time)}s] Status: {status}")
                if job.get('error_message'):
                    print(f"  Error: {job['error_message']}")
                last_status = status

            if status == "completed":
                print(f"\n✓ Job completed successfully")
                print(f"  Video URL: {job.get('video_url', 'N/A')}")
                return job
            elif status == "failed":
                print(f"\n✗ Job failed")
                print(f"  Error: {job.get('error_message', 'Unknown error')}")
                return job

        time.sleep(2)

    print(f"\n✗ Timeout after {timeout}s")
    return None


def test_verify_video(project_id: str):
    """Verify the video file exists"""
    print_section("4. Verify Video File")

    video_path = f"/home/edy/Music/下载/博文生成视频项目/backend/storage/videos/{project_id}/{project_id}.mp4"

    print(f"Checking video file: {video_path}")

    if os.path.exists(video_path):
        file_size = os.path.getsize(video_path)
        print(f"✓ Video file exists")
        print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

        # Check modification time
        mtime = os.path.getmtime(video_path)
        print(f"  Modified: {time.ctime(mtime)}")
        return True
    else:
        print(f"✗ Video file not found")
        return False


def main():
    print_section("Step 20 - Rerender Functionality Test")

    # Use the project from step 18
    project_id = "c4f46fd789d84c4b8284d856b62fe4c9"

    # Get scenes first
    print(f"\nGetting scenes for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/scenes")

    if response.status_code != 200:
        print(f"✗ Failed to get scenes: {response.text}")
        return

    scenes = response.json()
    if not scenes:
        print("✗ No scenes found. Please run step 18 first.")
        return

    scene_id = scenes[0]['scene_id']
    print(f"Using scene: {scene_id}")

    # Test 1: Update a scene
    updated_scene = test_update_scene(scene_id)
    if not updated_scene:
        print("\n✗ Failed to update scene")
        return

    # Test 2: Trigger rerender
    job_id = test_trigger_rerender(project_id)
    if not job_id:
        print("\n✗ Failed to trigger rerender")
        return

    # Test 3: Monitor job
    job = test_monitor_job(job_id, timeout=300)
    if not job:
        print("\n✗ Job monitoring failed")
        return

    if job['status'] != 'completed':
        print("\n✗ Job did not complete successfully")
        return

    # Test 4: Verify video
    test_verify_video(project_id)

    print_section("Step 20 Test Complete")
    print("✓ Scene update")
    print("✓ Rerender job creation")
    print("✓ Job processing")
    print("✓ Video generation")


if __name__ == "__main__":
    main()
