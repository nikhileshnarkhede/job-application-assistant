#!/usr/bin/env python3
"""
Resume Generator - Renders LaTeX resume from JSON data and Jinja2 template

Usage:
    python generate_resume.py resume_data.json resume_template.tex output.tex

Requirements:
    pip install jinja2
"""

import json
import argparse
from jinja2 import Environment, BaseLoader


def load_json(filepath: str) -> dict:
    """Load resume data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(filepath: str) -> str:
    """Load template content from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def render_resume(template_str: str, data: dict) -> str:
    """Render the resume using Jinja2 with LaTeX-safe delimiters."""
    # Custom delimiters to avoid LaTeX conflicts
    # Using [[ ]] for variables and [% %] for blocks
    env = Environment(
        loader=BaseLoader(),
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]',
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = env.from_string(template_str)
    return template.render(**data)


def save_output(content: str, filepath: str) -> None:
    """Save rendered resume to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Resume saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Generate LaTeX resume from JSON data')
    parser.add_argument('data', help='Path to JSON data file')
    parser.add_argument('template', help='Path to LaTeX template file')
    parser.add_argument('output', help='Path for output .tex file')
    
    args = parser.parse_args()
    
    # Load data and template
    print(f"Loading data from: {args.data}")
    data = load_json(args.data)
    
    print(f"Loading template from: {args.template}")
    template_str = load_template(args.template)
    
    # Render and save
    print("Rendering resume...")
    rendered = render_resume(template_str, data)
    
    save_output(rendered, args.output)
    print("\n✓ Done! Compile with: pdflatex", args.output)


if __name__ == '__main__':
    main()
