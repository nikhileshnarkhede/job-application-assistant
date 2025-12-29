"""
Pipeline Runner

Execution entry point with checkpointing support.
"""

import uuid
import time
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

from pipeline.config import PATHS_CONFIG
from pipeline.state import create_initial_state
from pipeline.graph import build_parent_graph


# Check if checkpointing is available
CHECKPOINTING_AVAILABLE = False
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    CHECKPOINTING_AVAILABLE = True
except ImportError:
    pass


def run_pipeline(
    jd_url: Optional[str] = None,
    jd_text: Optional[str] = None,
    resume_from: Optional[str] = None,
    enable_checkpoints: bool = True
) -> Dict[str, Any]:
    """
    Run the complete pipeline.
    
    Args:
        jd_url: URL to job posting
        jd_text: Raw job description text
        resume_from: Thread ID to resume from (optional)
        enable_checkpoints: Whether to enable checkpointing
        
    Returns:
        Dict with final state and execution info
    """
    start_time = time.time()
    thread_id = resume_from or str(uuid.uuid4())[:8]
    
    # Setup checkpointer
    checkpointer = None
    db_conn = None
    
    if enable_checkpoints and CHECKPOINTING_AVAILABLE:
        checkpoint_path = Path(PATHS_CONFIG["checkpoints_folder"])
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        db_path = checkpoint_path / "pipeline.db"
        
        print("🔨 Building pipeline graph with checkpointing...")
        print(f"   💾 Checkpoint DB: {db_path}")
        print(f"   🆔 Thread ID: {thread_id}")
        
        # Create connection and checkpointer properly
        db_conn = sqlite3.connect(str(db_path), check_same_thread=False)
        checkpointer = SqliteSaver(db_conn)
    else:
        print("🔨 Building pipeline graph (no checkpointing)...")
    
    try:
        # Build graph
        graph = build_parent_graph(checkpointer=checkpointer)
        
        # Prepare initial state
        initial_state = create_initial_state(jd_url=jd_url, jd_text=jd_text)
        
        # Config for invocation
        config = {"configurable": {"thread_id": thread_id}}
        
        print("\n🚀 Starting pipeline execution...")
        print("=" * 60)
        
        # Run the graph
        final_state = graph.invoke(initial_state, config)
        
        duration = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETED!")
        print("=" * 60)
        print(f"   ⏱️  Duration: {duration:.1f} seconds")
        print(f"   📊 ATS Score: {final_state.get('ats_score', 0):.1f}%")
        print(f"   📊 Compliance Score: {final_state.get('compliance_score', 0):.1f}%")
        print(f"   🆔 Thread ID: {thread_id}")
        
        if final_state.get('output_folder'):
            print(f"   📁 Outputs: {final_state.get('output_folder')}")
        
        return {
            "success": True,
            "state": final_state,
            "duration": duration,
            "thread_id": thread_id,
            "ats_score": final_state.get("ats_score", 0),
            "compliance_score": final_state.get("compliance_score", 0),
            "output_folder": final_state.get("output_folder", "")
        }
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "duration": duration,
            "thread_id": thread_id
        }
    
    finally:
        # Clean up connection
        if db_conn:
            db_conn.close()


def list_checkpoints() -> list:
    """
    List available checkpoint thread IDs.
    
    Returns:
        List of thread IDs that can be resumed
    """
    checkpoint_path = Path(PATHS_CONFIG["checkpoints_folder"]) / "pipeline.db"
    
    if not checkpoint_path.exists():
        print("⚠️  No checkpoint database found")
        return []
    
    try:
        conn = sqlite3.connect(str(checkpoint_path))
        cursor = conn.cursor()
        
        # Query for unique thread IDs
        cursor.execute("""
            SELECT DISTINCT thread_id 
            FROM checkpoints 
            ORDER BY thread_id
        """)
        
        threads = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"📋 Found {len(threads)} checkpoint threads:")
        for t in threads:
            print(f"   • {t}")
        
        return threads
        
    except Exception as e:
        print(f"⚠️  Error reading checkpoints: {e}")
        return []


def get_pipeline_status(thread_id: str) -> Dict[str, Any]:
    """
    Get the status of a pipeline run.
    
    Args:
        thread_id: Thread ID to check
        
    Returns:
        Dict with pipeline status info
    """
    if not CHECKPOINTING_AVAILABLE:
        return {"error": "Checkpointing not available"}
    
    checkpoint_path = Path(PATHS_CONFIG["checkpoints_folder"]) / "pipeline.db"
    
    if not checkpoint_path.exists():
        return {"error": "No checkpoint database found"}
    
    try:
        conn = sqlite3.connect(str(checkpoint_path))
        checkpointer = SqliteSaver(conn)
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get latest state
        state = checkpointer.get(config)
        conn.close()
        
        if state:
            return {
                "thread_id": thread_id,
                "current_stage": state.get("current_stage", "unknown"),
                "ats_score": state.get("ats_score", 0),
                "compliance_score": state.get("compliance_score", 0),
                "has_resume": state.get("resume_json") is not None,
                "has_cover_letter": bool(state.get("cover_letter_text")),
                "has_email": bool(state.get("email_text"))
            }
        
        return {"error": f"Thread {thread_id} not found"}
        
    except Exception as e:
        return {"error": str(e)}
