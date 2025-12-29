"""
Excel Writer Tool for MCP Server.

Provides Excel read/write operations using Pandas.
Manages the job application tracker spreadsheet.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd


# Default tracker columns
TRACKER_COLUMNS = [
    "thread_id",
    "date",
    "company",
    "job_title",
    "job_url",
    "location",
    "employment_type",
    "skills_matched",
    "skills_missing",
    "selected_projects",
    "ats_score",
    "resume_rubric_score",
    "cover_letter_rubric_score",
    "resume_version",
    "application_status",
    "follow_up_date",
    "notes",
]


def get_tracker_path() -> str:
    """Get the path to the Excel tracker file."""
    base_path = os.getenv("APPLICATIONS_PATH", "./applications")
    return os.path.join(base_path, "job_tracker.xlsx")


def create_tracker_if_not_exists(tracker_path: Optional[str] = None) -> str:
    """
    Create the tracker Excel file if it doesn't exist.
    
    Args:
        tracker_path: Optional custom path for the tracker
        
    Returns:
        Path to the tracker file
    """
    path = tracker_path or get_tracker_path()
    
    if not os.path.exists(path):
        # Create empty DataFrame with columns
        df = pd.DataFrame(columns=TRACKER_COLUMNS)
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write to Excel
        df.to_excel(path, index=False, engine="openpyxl")
    
    return path


def append_excel_row(
    row_data: Dict[str, Any],
    tracker_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Append a new row to the job tracker Excel file.
    
    Args:
        row_data: Dictionary containing row data
        tracker_path: Optional custom path for the tracker
        
    Returns:
        Dictionary with operation status and row index
    """
    path = create_tracker_if_not_exists(tracker_path)
    
    # Read existing data
    df = pd.read_excel(path, engine="openpyxl")
    
    # Prepare row with defaults
    new_row = {col: row_data.get(col, "") for col in TRACKER_COLUMNS}
    
    # Auto-fill date if not provided
    if not new_row.get("date"):
        new_row["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Convert lists to strings for Excel
    for key in ["skills_matched", "skills_missing", "selected_projects"]:
        if isinstance(new_row.get(key), list):
            new_row[key] = ", ".join(new_row[key])
    
    # Append row
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Write back to Excel
    df.to_excel(path, index=False, engine="openpyxl")
    
    return {
        "status": "success",
        "row_index": len(df) - 1,
        "tracker_path": path,
    }


def read_excel_sheet(
    tracker_path: Optional[str] = None,
    sheet_name: str = "Sheet1"
) -> List[Dict[str, Any]]:
    """
    Read the job tracker Excel file.
    
    Args:
        tracker_path: Optional custom path for the tracker
        sheet_name: Name of the sheet to read
        
    Returns:
        List of dictionaries, each representing a row
    """
    path = tracker_path or get_tracker_path()
    
    if not os.path.exists(path):
        return []
    
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    
    # Convert NaN to empty strings
    df = df.fillna("")
    
    return df.to_dict(orient="records")


def update_excel_row(
    thread_id: str,
    updates: Dict[str, Any],
    tracker_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a specific row in the tracker by thread_id.
    
    Args:
        thread_id: The thread ID to update
        updates: Dictionary of columns to update
        tracker_path: Optional custom path for the tracker
        
    Returns:
        Dictionary with operation status
    """
    path = tracker_path or get_tracker_path()
    
    if not os.path.exists(path):
        return {"status": "error", "message": "Tracker file not found"}
    
    df = pd.read_excel(path, engine="openpyxl")
    
    # Find the row with matching thread_id
    mask = df["thread_id"] == thread_id
    
    if not mask.any():
        return {"status": "error", "message": f"Thread {thread_id} not found"}
    
    # Update the row
    for col, value in updates.items():
        if col in df.columns:
            if isinstance(value, list):
                value = ", ".join(value)
            df.loc[mask, col] = value
    
    # Write back
    df.to_excel(path, index=False, engine="openpyxl")
    
    return {
        "status": "success",
        "thread_id": thread_id,
        "updated_columns": list(updates.keys()),
    }


def get_application_by_thread(
    thread_id: str,
    tracker_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get application data by thread ID.
    
    Args:
        thread_id: The thread ID to look up
        tracker_path: Optional custom path for the tracker
        
    Returns:
        Dictionary with application data, or None if not found
    """
    rows = read_excel_sheet(tracker_path)
    
    for row in rows:
        if row.get("thread_id") == thread_id:
            return row
    
    return None


def get_applications_by_status(
    status: str,
    tracker_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all applications with a specific status.
    
    Args:
        status: The status to filter by
        tracker_path: Optional custom path for the tracker
        
    Returns:
        List of matching application dictionaries
    """
    rows = read_excel_sheet(tracker_path)
    return [row for row in rows if row.get("application_status") == status]


def get_tracker_statistics(tracker_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics about the job tracker.
    
    Args:
        tracker_path: Optional custom path for the tracker
        
    Returns:
        Dictionary with tracker statistics
    """
    rows = read_excel_sheet(tracker_path)
    
    if not rows:
        return {
            "total_applications": 0,
            "by_status": {},
            "average_ats_score": 0,
        }
    
    df = pd.DataFrame(rows)
    
    # Count by status
    status_counts = df["application_status"].value_counts().to_dict()
    
    # Average ATS score (only for numeric values)
    ats_scores = pd.to_numeric(df["ats_score"], errors="coerce")
    avg_ats = ats_scores.mean() if not ats_scores.isna().all() else 0
    
    return {
        "total_applications": len(rows),
        "by_status": status_counts,
        "average_ats_score": round(avg_ats, 2),
    }


if __name__ == "__main__":
    # Test Excel writer
    print("Testing Excel Writer...")
    
    # Create test tracker
    test_path = "/tmp/test_tracker.xlsx"
    
    # Test append
    result = append_excel_row(
        {
            "thread_id": "test-123",
            "company": "Test Company",
            "job_title": "ML Engineer",
            "skills_matched": ["Python", "TensorFlow"],
            "ats_score": 92,
        },
        tracker_path=test_path
    )
    print(f"Append test: {result['status']}")
    
    # Test read
    rows = read_excel_sheet(tracker_path=test_path)
    print(f"Read test: {len(rows)} rows")
    
    # Test update
    result = update_excel_row(
        "test-123",
        {"application_status": "Applied"},
        tracker_path=test_path
    )
    print(f"Update test: {result['status']}")
    
    # Clean up
    os.remove(test_path)
    print("Excel Writer tests complete!")
