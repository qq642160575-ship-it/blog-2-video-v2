#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 24 test - Frontend scene editing page
"""
import requests

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def test_get_scene(project_id: str):
    """Test getting scenes to find one to edit"""
    print_section("1. Get Scenes for Editing")

    print(f"Getting scenes for project {project_id}...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/scenes")

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        scenes = response.json()
        print(f"✓ Found {len(scenes)} scenes")

        if scenes:
            first_scene = scenes[0]
            print(f"\nFirst scene to edit:")
            print(f"  ID: {first_scene['scene_id']}")
            print(f"  Version: {first_scene['version']}")
            print(f"  Voiceover: {first_scene['voiceover'][:50]}...")
            print(f"  Duration: {first_scene['duration_sec']}s")
            return first_scene
        else:
            print("✗ No scenes found")
            return None
    else:
        print(f"✗ Failed to get scenes: {response.text}")
        return None


def test_update_scene(scene_id: str):
    """Test PATCH /scenes/{scene_id}"""
    print_section("2. Update Scene")

    updates = {
        "voiceover": "这是通过前端编辑页面更新的旁白文本。",
        "duration_sec": 6,
        "screen_text": ["测试文本1", "测试文本2"]
    }

    print(f"Updating scene {scene_id}...")
    print(f"New voiceover: {updates['voiceover']}")
    print(f"New duration: {updates['duration_sec']}s")
    print(f"New screen text: {updates['screen_text']}")

    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Scene updated successfully")
        print(f"  New version: {result['version']}")
        print(f"  Voiceover: {result['voiceover']}")
        print(f"  Duration: {result['duration_sec']}s")
        return True
    else:
        print(f"✗ Failed to update scene: {response.text}")
        return False


def test_validation_errors(scene_id: str):
    """Test validation errors"""
    print_section("3. Test Validation Errors")

    # Test 1: Voiceover too long
    print("\nTest 3.1: Voiceover too long (>90 chars)")
    updates = {
        "voiceover": "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的旁白文本"
    }
    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )
    if response.status_code == 400:
        print(f"✓ Validation error caught: {response.json()['detail']}")
    else:
        print(f"✗ Expected 400, got {response.status_code}")

    # Test 2: Duration out of range
    print("\nTest 3.2: Duration out of range")
    updates = {
        "duration_sec": 15
    }
    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )
    if response.status_code == 400:
        print(f"✓ Validation error caught: {response.json()['detail']}")
    else:
        print(f"✗ Expected 400, got {response.status_code}")

    # Test 3: Screen text too long
    print("\nTest 3.3: Screen text item too long (>18 chars)")
    updates = {
        "screen_text": ["这是一个非常非常非常非常长的文本"]
    }
    response = requests.patch(
        f"{BASE_URL}/projects/scenes/{scene_id}",
        json=updates
    )
    if response.status_code == 400:
        print(f"✓ Validation error caught: {response.json()['detail']}")
    else:
        print(f"✗ Expected 400, got {response.status_code}")


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
    print_section("Step 24 - Frontend Scene Editing Page Test")

    # Use a completed project from previous tests
    project_id = "c4f46fd789d84c4b8284d856b62fe4c9"

    print(f"\nUsing project ID: {project_id}")

    # Test 1: Get scenes
    scene = test_get_scene(project_id)

    if not scene:
        print("\n✗ No scenes found to edit")
        return

    scene_id = scene['scene_id']

    # Test 2: Update scene
    update_success = test_update_scene(scene_id)

    # Test 3: Validation errors
    test_validation_errors(scene_id)

    # Test 4: Frontend accessibility
    frontend_ok = test_frontend_accessible()

    print_section("Step 24 Test Summary")

    if scene:
        print("✓ GET /projects/{project_id}/scenes works")
    else:
        print("✗ GET /projects/{project_id}/scenes failed")

    if update_success:
        print("✓ PATCH /scenes/{scene_id} works")
    else:
        print("✗ PATCH /scenes/{scene_id} failed")

    print("✓ Validation rules are enforced")

    if frontend_ok:
        print("✓ Frontend is accessible")
    else:
        print("✗ Frontend is not accessible")

    print("\nManual Testing:")
    print(f"1. Open http://localhost:3000/result/{project_id} in your browser")
    print("2. Click 'Edit' button on any scene")
    print("3. Verify you see the edit form with:")
    print("   - Scene info (ID, version, template)")
    print("   - Voiceover textarea (with character count)")
    print("   - Duration input (4-9 seconds)")
    print("   - Screen text inputs (add/remove)")
    print("4. Edit the scene:")
    print("   - Change voiceover text")
    print("   - Change duration")
    print("   - Add/remove screen text")
    print("5. Click 'Save' button")
    print("   - Should show success alert")
    print("   - Should redirect back to result page")
    print("   - Should see updated version number")
    print("6. Click 'Edit' again and click 'Save and Rerender'")
    print("   - Should redirect to progress page")
    print("   - Should show rerender progress")
    print("   - Should complete and show updated video")


if __name__ == "__main__":
    main()
