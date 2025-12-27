import os
import sys
import uuid

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain_controller import BrainController

def test_roles():
    print("Starting Role Enforcement Test...")
    
    # Initialize BrainController
    # Ensure env vars are set for local testing
    os.environ["SKIP_AUTH"] = "true"
    os.environ["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "https://bebcwczcdpvrgmhzeyos.supabase.co")
    os.environ["SUPABASE_KEY"] = os.environ.get("SUPABASE_KEY", "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE")
    
    brain = BrainController(base_dir=".")
    
    # Mock User IDs
    creator_id = str(uuid.uuid4())
    editor_id = str(uuid.uuid4())
    admin_id = str(uuid.uuid4())
    
    # 1. Setup Roles in DB
    print("Step 1: Setting up roles in DB")
    brain.db.client.table("user_roles").insert([
        {"user_id": creator_id, "role": "CREATOR"},
        {"user_id": editor_id, "role": "EDITOR"},
        {"user_id": admin_id, "role": "ADMIN"}
    ]).execute()
    
    # 2. Test CREATOR permissions
    print("Step 2: Testing CREATOR permissions")
    assert brain.check_role(creator_id, ["CREATOR"]) == True
    assert brain.check_role(creator_id, ["ADMIN"]) == False
    
    # 3. Test EDITOR permissions
    print("Step 3: Testing EDITOR permissions")
    assert brain.check_role(editor_id, ["EDITOR"]) == True
    assert brain.check_role(editor_id, ["CREATOR"]) == False
    
    # 4. Test ADMIN permissions
    print("Step 4: Testing ADMIN permissions")
    assert brain.check_role(admin_id, ["ADMIN"]) == True
    assert brain.check_role(admin_id, ["CREATOR"]) == False
    
    # 5. Test multi-role check
    print("Step 5: Testing multi-role check")
    assert brain.check_role(editor_id, ["CREATOR", "EDITOR"]) == True
    assert brain.check_role(admin_id, ["CREATOR", "EDITOR"]) == False
    
    print("Role Enforcement Test Passed!")

if __name__ == "__main__":
    try:
        test_roles()
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
