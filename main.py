#!/usr/bin/env python3
"""
Job Application Assistant - CLI

Usage:
    python main.py --jd-url "https://..."
    python main.py --jd-text "Job description text..."
    python main.py --test
    python main.py --resume THREAD_ID
    python main.py --list-checkpoints
    python main.py --config
"""

import argparse
import sys
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Job Application Assistant Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --test                    Run with test JD URL
  python main.py --jd-url "https://..."    Process specific job URL
  python main.py --list-checkpoints        Show resumable runs
  python main.py --resume abc123           Resume from checkpoint
  python main.py --config                  Show configuration
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--jd-url",
        type=str,
        help="URL to job posting"
    )
    input_group.add_argument(
        "--jd-text",
        type=str,
        help="Raw job description text"
    )
    input_group.add_argument(
        "--test",
        action="store_true",
        help="Run with standard test JD URL"
    )
    
    # Checkpoint options
    parser.add_argument(
        "--resume",
        type=str,
        metavar="THREAD_ID",
        help="Resume from checkpoint thread ID"
    )
    parser.add_argument(
        "--list-checkpoints",
        action="store_true",
        help="List available checkpoints"
    )
    
    # Other options
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show configuration summary"
    )
    parser.add_argument(
        "--no-checkpoints",
        action="store_true",
        help="Disable checkpointing"
    )
    
    args = parser.parse_args()
    
    # Verify API key is loaded
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("   Make sure .env file exists and contains OPENAI_API_KEY")
        return 1
    
    # Handle --config
    if args.config:
        from pipeline import print_config_summary
        print_config_summary()
        print(f"\n🔑 OpenAI API Key: {os.getenv('OPENAI_API_KEY', '')[:20]}...")
        return 0
    
    # Handle --list-checkpoints
    if args.list_checkpoints:
        from pipeline import list_checkpoints
        list_checkpoints()
        return 0
    
    # Handle --test
    if args.test:
        from subgraphs.test_constants import STANDARD_JD_URL
        args.jd_url = STANDARD_JD_URL
        print(f"🧪 Test mode: Using {STANDARD_JD_URL}")
    
    # Require input
    if not args.jd_url and not args.jd_text and not args.resume:
        parser.print_help()
        print("\n❌ Error: Provide --jd-url, --jd-text, --test, or --resume")
        return 1
    
    # Run pipeline
    from pipeline import run_pipeline
    
    result = run_pipeline(
        jd_url=args.jd_url,
        jd_text=args.jd_text,
        resume_from=args.resume,
        enable_checkpoints=not args.no_checkpoints
    )
    
    if result["success"]:
        return 0
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
