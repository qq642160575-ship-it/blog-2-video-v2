#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 23 test - Frontend result preview page
"""
import requests

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_get_result(project_id: str):
    """Test GET /projects/{project_id}/result"""
    print_section("1. Get Project Result")

    print(f"Getting result for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/result")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Result retrieved successfully")
        print(f"  Video URL: {result.get('video_url', 'N/A')}")
        print(f"  Status: {result.get('status', 'N/A')}")
        return result
    else:
        print(f"✗ Failed to get result: {response.text}")
        return None


def test_get_scenes(project_id: str):
    """Test GET /projects/{project_id}/scenes"""
    print_section("2. Get Project Scenes")

    print(f"Getting scenes for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/scenes")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        scenes = response.json()
        print(f"✓ Scenes retrieved successfully")
        print(f"  Total scenes: {len(scenes)}")

        if scenes:
            first_scene = scenes[0]
            print(f"\n  First scene:")
            print(f"    ID: {first_scene['scene_id']}")
            print(f"    Version: {first_scene['version']}")
            print(f"    Template: {first_scene['template_type']}")
            print(f"    Duration: {first_scene['duration_sec']}s")
            print(f"    Voiceover: {first_scene['voiceover'][:50]}...")

        return scenes
    else:
        print(f"✗ Failed to get scenes: {response.text}")
        return None


def test_video_file_exists(video_url: str):
    """Test if video file is accessible"""
    print_section("3. Video File Accessibility")

    if not video_url:
        print("✗ No video URL provided")
        return False

    full_url = f"{BASE_URL}/{video_url}"
    print(f"Checking video file: {full_url}")

    try:
        response = requests.head(full_url)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            content_length = response.headers.get('Content-Length', 'Unknown')
            content_type = response.headers.get('Content-Type', 'Unknown')
            print(f"✓ Video file is accessible")
            print(f"  Content-Type: {content_type}")
            print(f"  Content-Length: {content_length} bytes")
            return True
        else:
            print(f"✗ Video file not accessible")
            return False
    except Exception as e:
        print(f"✗ Error checking video file: {e}")
        return False


def test_frontend_accessible():
    """Test if frontend is accessible"""
    print_section("4. Frontend Accessibility")

    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"✗ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot access frontend: {e}")
        return False


def main():
    print_section("Step 23 - Frontend Result Preview Page Test")

    # Use a completed project from previous tests
    # You may need to update this project_id
    project_id = "c4f46fd789d84c4b8284d856b62fe4c9"

    print(f"\nUsing project ID: {project_id}")
    print("Note: This project should have a completed video")

    # Test 1: Get result
    result = test_get_result(project_id)

    # Test 2: Get scenes
    scenes = test_get_scenes(project_id)

    # Test 3: Check video file
    video_accessible = False
    if result and result.get('video_url'):
        video_accessible = test_video_file_exists(result['video_url'])

    # Test 4: Frontend accessibility
    frontend_ok = test_frontend_accessible()

    print_section("Step 23 Test Summary")

    if result:
        print("✓ GET /projects/{project_id}/result works")
    else:
        print("✗ GET /projects/{project_id}/result failed")

    if scenes:
        print(f"✓ GET /projects/{{project_id}}/scenes works ({len(scenes)} scenes)")
    else:
        print("✗ GET /projects/{project_id}/scenes failed")

    if video_accessible:
        print("✓ Video file is accessible")
    else:
        print("✗ Video file is not accessible")

    if frontend_ok:
        print("✓ Frontend is accessible")
    else:
        print("✗ Frontend is not accessible")

    print("\nManual Testing:")
    print(f"1. Open http://localhost:3000/result/{project_id} in your browser")
    print("2. Verify you see:")
    print("   - Video player with the generated video")
    print("   - 'Re-render' and 'Create New Project' buttons")
    print("   - Scene list showing all scenes")
    print("   - Each scene showing:")
    print("     - Scene number and version")
    print("     - Template type and duration")
    print("     - Voiceover text")
    print("     - Screen text (if any)")
    print("3. Test video playback")
    print("4. Click 'Re-render' button (should redirect to progress page)")
    print("5. Click 'Create New Project' button (should redirect to home)")


if __name__ == "__main__":
    main()
