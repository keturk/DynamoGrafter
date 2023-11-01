# MIT License
#
# Copyright (c) 2023 Kamil Ercan Turkarslan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import logging
import click
from yaml_parser import parse_yaml_file
from graph_generator import generate_html_label, generate_graph_from_yaml

# Constants and Configurations
OUTPUT_EXTENSION = '.graph'

# Initialize logging
logging.basicConfig(level=logging.INFO)


# Function to generate an output file path
def generate_output_filepath(input_filepath, output_dir):
    filename_without_extension = os.path.splitext(os.path.basename(input_filepath))[0]
    return os.path.join(output_dir, filename_without_extension + OUTPUT_EXTENSION)


# Command line interface
@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output-dir', type=click.Path(), default='.', help='Directory to save the output graph. Default is the current directory.')
@click.option('--force', is_flag=True, help='Overwrite without asking for confirmation.')
def main(file_path, output_dir, force):
    yaml_data = parse_yaml_file(file_path)
    output_filepath = generate_output_filepath(file_path, output_dir)
    dot = generate_graph_from_yaml(yaml_data)

    if not force and os.path.exists(output_filepath):
        confirmation = input(f"File '{output_filepath}' already exists. Overwrite? (y/n): ").strip().lower()
        if confirmation != 'y':
            logging.info("Graph generation canceled.")
            return

    dot.render(output_filepath, view=True)
    logging.info(f"Graph saved to '{output_filepath}'")


if __name__ == "__main__":
    main()