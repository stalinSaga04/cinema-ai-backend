import os
import sys
import uuid

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain_controller import BrainController, ProjectStatus

def test_ai_pause():
    print("Starting AI Pause Test...")
    
    # Initialize BrainController
    os.environ["SKIP_AUTH"] = "true"
    os.environ["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "https://bebcwczcdpvrgmhzeyos.supabase.co")
    os.environ["SUPABASE_KEY"] = os.environ.get("SUPABASE_KEY", "sb_publishable_WhyhXpfQ0ZJuZsqJYrJtLw_48Crs5RE")
    
    brain = BrainController(base_dir=".")
    
    project_id = str(uuid.uuid4())
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # 1. Create Project
    print(f"Step 1: Creating project {project_id}")
    brain.db.create_project(project_id, "AI Pause Test", user_id)
    
    # 2. Trigger Completion Logic (which triggers AI Pause)
    print("Step 2: Triggering project completion (AI Pause)")
    brain._check_project_completion(project_id)
    
    # 3. Verify Status
    status = brain.db.get_project_status(project_id)
    print(f"Status: {status}")
    assert status == ProjectStatus.WAITING_APPROVAL.value
    
    # 4. Verify Questions
    print("Step 4: Verifying questions in DB")
    questions = brain.db.get_project_questions(project_id)
    print(f"Questions: {questions}")
    assert len(questions) == 3
    assert "Is the pacing OK?" in questions
    
    print("AI Pause Test Passed!")

if __name__ == "__main__":
    try:
        test_ai_pause()
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
