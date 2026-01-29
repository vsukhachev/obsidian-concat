#!/usr/bin/env python3
"""
Obsidian Markdown Concatenation Utility

Scans a directory for all .md files (recursively) and concatenates
them into a single output file.
"""

import argparse
import sys
from pathlib import Path
from typing import List


def scan_markdown_files(directory: Path) -> List[Path]:
    """
    Recursively scan directory for all .md files.
    
    Args:
        directory: Path object pointing to the directory to scan
        
    Returns:
        List of Path objects for all found .md files, sorted alphabetically
    """
    try:
        md_files = sorted(directory.rglob('*.md'))
        return md_files
    except PermissionError as e:
        print(f"Error: Permission denied while scanning directory: {e}", file=sys.stderr)
        sys.exit(1)


def concatenate_files(md_files: List[Path], output_file: Path, base_dir: Path) -> None:
    """
    Read all markdown files and concatenate them into a single output file.
    
    Args:
        md_files: List of Path objects for markdown files to concatenate
        output_file: Path object for the output file
        base_dir: Base directory for relative path calculation
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, md_file in enumerate(md_files):
                # Skip the output file if it's in the same directory
                if md_file.resolve() == output_file.resolve():
                    continue
                
                try:
                    # Calculate relative path for better readability
                    try:
                        relative_path = md_file.relative_to(base_dir)
                    except ValueError:
                        relative_path = md_file
                    
                    # Add separator with file name
                    separator = f"\n{'='*80}\n"
                    separator += f"File: {relative_path}\n"
                    separator += f"{'='*80}\n\n"
                    
                    if i > 0:
                        outfile.write("\n\n")
                    
                    outfile.write(separator)
                    
                    # Read and write file content
                    with open(md_file, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        
                except PermissionError:
                    print(f"Warning: Permission denied reading file: {md_file}", file=sys.stderr)
                    continue
                except UnicodeDecodeError:
                    print(f"Warning: Unable to decode file (invalid UTF-8): {md_file}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Warning: Error reading file {md_file}: {e}", file=sys.stderr)
                    continue
                    
        print(f"Successfully concatenated {len(md_files)} file(s) into: {output_file}")
        
    except PermissionError:
        print(f"Error: Permission denied writing to output file: {output_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the CLI utility."""
    parser = argparse.ArgumentParser(
        description='Concatenate all Markdown files from a directory into a single file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python concat.py
  python concat.py --input sample
  python concat.py --input sample --output result.md
  python concat.py -i ./notes -o combined_notes.md
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        default='.',
        help='Input directory to scan for .md files (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='combined.md',
        help='Output file path (default: combined.md)'
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    input_dir = Path(args.input).resolve()
    output_file = Path(args.output).resolve()
    
    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Scan for markdown files
    print(f"Scanning directory: {input_dir}")
    md_files = scan_markdown_files(input_dir)
    
    # Filter out the output file if it exists in the scan results
    md_files = [f for f in md_files if f.resolve() != output_file.resolve()]
    
    if not md_files:
        print(f"Warning: No .md files found in directory: {input_dir}", file=sys.stderr)
        sys.exit(0)
    
    print(f"Found {len(md_files)} markdown file(s)")
    
    # Concatenate files
    concatenate_files(md_files, output_file, input_dir)


if __name__ == '__main__':
    main()
