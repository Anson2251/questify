from latex_frontend import markdown2latex
from utils import read_sql_file, create_dir_if_not_exist
import subprocess
import os
from datetime import datetime
import pathlib
import re

import sqlite3
from sqlite3 import Connection


def compile_latex(latex_file: str, output_dir: str = None):
	"""
	Compile a LaTeX file to PDF using pdflatex.

	Args:
		latex_file (str): Path to the LaTeX file to compile.
		output_dir (str, optional): Directory to save the output files. If None,
									the output files will be saved in the same
									directory as the LaTeX file.
	"""
	# Prepare the command with the output directory if specified
	command = ['pdflatex', '-interaction=nonstopmode']
	if output_dir:
		command.extend(['-output-directory', output_dir])
	command.append(latex_file)

	# Run the pdflatex command
	subprocess.run(
		command,
		check=True,
		input="",  # Send empty input to avoid hanging
		text=True,  # Ensure input is treated as text
		capture_output=True  # Capture output for debugging
	)

def into_minipage(latex_code: str):
	return f"\\begin{{minipage}}{{\\textwidth}}\n{latex_code.strip()}\n\\end{{minipage}}"

def into_document(latex_code: str, title: str):
	latex = f"""
\\documentclass{{article}}
\\usepackage[a4paper, margin=1in]{{geometry}}

\\title{{{title}}}
\\author{{{os.getlogin()}}}
\\date{{\\today}}

\\begin{{document}}
\\setlength{{\\parindent}}{{0pt}}
\\maketitle
\\newpage
{latex_code.strip()}
\\end{{document}}
"""
	latex = latex.strip()
	return re.sub(pattern=r'(\\newline|\\\\)\s*(\\newline|\\\\)', repl="\\\\newline", string=latex)

def compile_latex_to_pdf(latex_file, output_dir=None):
	# Ensure the file exists
	if not os.path.isfile(latex_file):
		print(f"Error: The file {latex_file} does not exist.")
		return

	try:
		# First pass to generate the PDF and auxiliary files
		compile_latex(latex_file, output_dir)

		# Second pass to resolve references (e.g., cross-references)
		compile_latex(latex_file, output_dir)

		print(f"Successfully compiled {latex_file} to PDF.")
	except subprocess.CalledProcessError as e:
		print(f"Error during compilation: {e}")
		print(f"Output: {e.stdout}")
		print(f"Errors: {e.stderr}")
	except FileNotFoundError:
		print("Error: pdflatex is not installed or not in your PATH.")

if __name__ == "__main__":
	syllabus_criteria = input("Enter the syllabus criteria (Support GLOB): ")
	relevance_criteria = input("Enter the minimum relevance criteria: ")

	path = f"compile/{datetime.now().strftime('%Y%m%d-%H%M%S')}/"
	query = read_sql_file("src/queries/select-exercises-by-syllabus.sql")

	conn = sqlite3.connect("./papers.db")
	cursor = conn.cursor()
	cursor.execute(query, (syllabus_criteria, float(relevance_criteria)))
	matched = [{"id": i[0], "description": markdown2latex(i[1]), "relevance": i[2]} for i in cursor.fetchall()]
	latex = ""
	counter = 0
	syllabus = matched[0]["id"].split("-")[0]
	for item in matched:
		meta = item["id"].split("-")
		header = f"[{meta[0]}/{meta[1]}/{meta[2]}/{'-'.join(meta[3:])}]"
		content = f"\\textbf{{{str(counter + 1)}.}} {item['description'].strip()}"
		latex += into_minipage(f"\\texttt{{{header}}} \\newline\n{content}\n\n")
		latex += "\\newline\\vspace{1cm}\n\n"
		counter += 1

	latex = into_document(latex, f"Topic Questions on {syllabus}")

	create_dir_if_not_exist("compile")
	create_dir_if_not_exist(path)
	latex_file = path + "paper.tex"
	pathlib.Path(latex_file).write_text(latex)
	print("Compiled LaTeX file to: ", latex_file)
	compile_latex_to_pdf(latex_file, path)



	# compile_latex_to_pdf(latex_file)
