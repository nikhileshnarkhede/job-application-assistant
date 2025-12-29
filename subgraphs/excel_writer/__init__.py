"""
Excel Writer Subgraph

Saves job application data to Excel tracking spreadsheet:
1. Application details (company, role, date, status)
2. Resume and cover letter versions/scores
3. Contact information
4. Follow-up tracking
5. Notes and outcomes

Usage:
    from subgraphs.excel_writer import (
        save_application_to_excel,
        quick_save_application,
        update_application_status,
        get_applications_summary,
        ApplicationStatus,
        ApplicationSource
    )
    
    # Save from full pipeline
    result = save_application_to_excel(
        structured_jd=structured_jd,
        resume_json=resume_json,
        resume_score=85.5,
        cover_letter_score=82.0,
        status=ApplicationStatus.APPLIED,
        source=ApplicationSource.LINKEDIN
    )
    
    # Quick save
    result = quick_save_application(
        company="Google",
        role="Senior ML Engineer",
        job_url="https://careers.google.com/...",
        status=ApplicationStatus.APPLIED
    )
    
    # Update status
    update_application_status(
        file_path="job_applications.xlsx",
        application_id="APP-20240115120000",
        new_status=ApplicationStatus.PHONE_SCREEN,
        notes="Scheduled for Jan 20"
    )
    
    # Get summary
    print(get_applications_summary("job_applications.xlsx"))
"""

from subgraphs.excel_writer.graph import (
    build_excel_writer_graph,
    create_excel_writer_subgraph,
    save_application_to_excel,
    quick_save_application,
    update_application_status,
    get_application_stats,
    get_applications_summary
)

from subgraphs.excel_writer.state import (
    ExcelWriterState,
    ApplicationStatus,
    ApplicationSource,
    ApplicationRecord,
    SpreadsheetConfig,
    SPREADSHEET_COLUMNS,
    generate_application_id,
    get_today
)

from subgraphs.excel_writer.nodes import (
    prepare_record,
    load_or_create_workbook,
    write_record,
    format_spreadsheet,
    save_workbook
)

__all__ = [
    # Main functions
    "save_application_to_excel",
    "quick_save_application",
    "update_application_status",
    "get_application_stats",
    "get_applications_summary",
    
    # Graph builders
    "build_excel_writer_graph",
    "create_excel_writer_subgraph",
    
    # State & Models
    "ExcelWriterState",
    "ApplicationStatus",
    "ApplicationSource",
    "ApplicationRecord",
    "SpreadsheetConfig",
    "SPREADSHEET_COLUMNS",
    "generate_application_id",
    "get_today",
    
    # Nodes
    "prepare_record",
    "load_or_create_workbook",
    "write_record",
    "format_spreadsheet",
    "save_workbook"
]
