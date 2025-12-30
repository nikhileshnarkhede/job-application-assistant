# Streamlit GUI - Job Application Assistant

A user-friendly web interface for the Job Application Assistant pipeline.

## Pages

| Page | Description |
|------|-------------|
| 🏠 **Home** | Dashboard with overview and quick navigation |
| ⚙️ **Configure** | Adjust pipeline parameters (experiences, ATS target, etc.) |
| 🚀 **Run Pipeline** | Input JD (URL or text) and execute pipeline |
| 📄 **Resume** | View and copy generated resume content |
| ✉️ **Cover Letter & Email** | View and copy cover letter and email |

## Running the App

```bash
# From project root
cd D:\ML_AI\LLM\job-application-assistant

# Activate virtual environment
venv\Scripts\activate

# Run Streamlit
streamlit run streamlit_app/app.py
```

The app will open at `http://localhost:8501`

## Features

### Configuration Page
- Adjust resume limits (experiences, projects)
- Set ATS target score and iterations
- Configure cover letter tone
- Enable/disable features (email, Excel tracking)
- View environment variable status

### Run Pipeline Page
- Input JD via URL or text paste
- Quick test buttons with sample JDs
- Real-time progress display
- View scores and outputs after completion

### Resume Page
- Full resume in copy-ready format
- Separate tabs for header, experience, skills
- Download as TXT, MD, or JSON
- View raw JSON for debugging

### Cover Letter & Email Page
- Full text with word count
- Download options
- Analysis of key elements
- Email tips and templates

## Session State

The app uses Streamlit session state to persist:
- `config` - User configuration settings
- `pipeline_result` - Last pipeline execution result
- `final_state` - Complete state from pipeline
- `pipeline_running` - Execution status flag

## File Structure

```
streamlit_app/
├── app.py                    # Main entry point (Home page)
├── README.md                 # This file
└── pages/
    ├── 1_⚙️_Configure.py     # Configuration page
    ├── 2_🚀_Run_Pipeline.py  # Pipeline execution page
    ├── 3_📄_Resume.py        # Resume display page
    └── 4_✉️_Cover_Letter_Email.py  # Cover letter & email page
```

## Requirements

Streamlit should already be in requirements.txt. If not:

```bash
pip install streamlit
```

## Screenshots

### Home Page
- Overview of pipeline stages
- Quick navigation buttons
- Current configuration summary

### Run Pipeline
- URL/Text input toggle
- Test JD buttons
- Progress bar during execution
- Results summary with scores

### Resume View
- Copy-ready text format
- Tabbed sections
- Download buttons
- JSON view
