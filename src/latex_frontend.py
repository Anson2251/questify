from typing import Any, Dict, Iterable, cast
import mistune
import re

from mistune.core import BaseRenderer, BlockState
from mistune.util import strip_end
from mistune.plugins.table import table
from mistune.plugins.math import math

# <answer-area size="<integer>"/>
answer_area_regexp = re.compile(r'<answer-area size="(\d+)"\s*\/>')

# <figure description="<string>" id="<string>"/>
figure_regexp = re.compile(r'<figure description="([^"]+)" id="([^"]+)"\s*\/>')

def handle_custom_tags_to_latex(html_code: str):
	answer_area_match = re.match(answer_area_regexp, html_code)
	if answer_area_match:
		size = int(answer_area_match.group(1))
		return "\n\\newline" + "\n".join(["\\parbox[t][2em][c]{\\linewidth}{\\dotfill}"] * size)

	figure_match = re.match(figure_regexp, html_code)
	if figure_match:
		description = figure_match.group(1)
		id = figure_match.group(2)
		return f"""
\\begin{{minipage}}[t]{{\\linewidth}}
  \\begin{{center}}
    \\fbox{{\\rule{{0pt}}{{2cm}} \\rule{{5cm}}{{0pt}}}}
  \\end{{center}}
  \\captionof{{figure}}{{{description}}}
  \\label{{fig:{id}}}
\\end{{minipage}}
"""


def to_escaped_code(code: str) -> str:
	return code.replace("\\", "\\textbackslash{}") \
		.replace("{", "\\{") \
		.replace("}", "\\}") \
		.replace("$", "\\$") \
		.replace("&", "\\&") \
		.replace("#", "\\#") \
		.replace("^", "\\^{}") \
		.replace("_", "\\_") \
		.replace("~", "\\~{}") \
		.replace("%", "\\%") \

def render_list(
	renderer: "BaseRenderer", token: Dict[str, Any], state: "BlockState"
) -> str:
	attrs = token["attrs"]
	if attrs["ordered"]:
		children = _render_ordered_list(renderer, token, state)
	else:
		children = _render_unordered_list(renderer, token, state)

	text = "".join(children)
	parent = token.get("parent")
	if parent:
		if parent["tight"]:
			return text
		return text + "\n"
	return strip_end(text) + "\n"

def _render_list_item(
	renderer: "BaseRenderer",
	parent: Dict[str, Any],
	item: Dict[str, Any],
	state: "BlockState",
) -> str:
	text = ""
	for tok in item["children"]:
		if tok["type"] == "list":
			tok["parent"] = parent
		elif tok["type"] == "blank_line":
			continue
		text += renderer.render_token(tok, state)

	lines = text.splitlines()
	text = (lines[0] if lines else "") + "\n"
	for line in lines[1:]:
		if line:
			text += " " * 4 + line + "\n"  # Indent subsequent lines
		else:
			text += "\n"

	return "\\item " + text.strip().rstrip("\\") + "\n"

def _render_ordered_list(
	renderer: "BaseRenderer", token: Dict[str, Any], state: "BlockState"
) -> Iterable[str]:
	attrs = token["attrs"]
	start = attrs.get("start", 1)
	yield "\\begin{enumerate}\n"
	for item in token["children"]:
		yield _render_list_item(renderer, {"tight": token["tight"]}, item, state)
		start += 1
	yield "\\end{enumerate}\n"


def _render_unordered_list(
	renderer: "BaseRenderer", token: Dict[str, Any], state: "BlockState"
) -> Iterable[str]:
	yield "\\begin{itemize}\n"
	for item in token["children"]:
		yield _render_list_item(renderer, {"tight": token["tight"]}, item, state)
	yield "\\end{itemize}\n"



def extract_text_from_cell(cell):
	text = ""
	for child in cell.get("children", []):
		if child["type"] == "text":
			text += child["raw"]
	return text.strip()

def generate_latex_table(table_dict):
	table_head = table_dict["children"][0]
	table_body = table_dict["children"][1]

	num_columns = len(table_head["children"])

	alignments = ["l"] * num_columns

	latex_table = "\n\\begin{tabular}{" + " ".join(alignments) + "}\n"
	latex_table += "\\hline\n"

	header_cells = []
	for cell in table_head["children"]:
		header_cells.append("\\textbf{" + extract_text_from_cell(cell) + "}")
	latex_table += " & ".join(header_cells) + " \\\\\n"
	latex_table += "\\hline\n"
	latex_table += "\\hline\n"

	for row in table_body["children"]:
		row_cells = []
		for cell in row["children"]:
			row_cells.append(extract_text_from_cell(cell))
		latex_table += " & ".join(row_cells) + " \\\\\n"
		latex_table += "\\hline\n"

	latex_table += "\\end{tabular}\n\\newline\\newline\n\n"
	return latex_table


class LaTeXRenderer(BaseRenderer):
	"""A renderer to re-format Markdown text."""

	NAME = "latex"

	def __call__(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> str:
		out = self.render_tokens(tokens, state)
		# special handle for line breaks
		out += "\n\n".join(self.render_referrences(state)) + "\n"
		# remove redundant empty lines
		out = "\n\n".join(
			map(
				lambda s: s.strip(),
				filter(lambda x: len(x.strip()) > 0, out.split("\n\n")),
			)
		)
		return out.strip()

	def render_referrences(self, state: BlockState) -> Iterable[str]:
		ref_links = state.env["ref_links"]
		for key in ref_links:
			attrs = ref_links[key]
			label = attrs["label"]
			url = attrs["url"]
			title = attrs.get("title")

			# LaTeX format for a hyperlink
			if title:
				text = f"\\href{{{url}}}{{{label}}} \\footnote{{{title}}}"
			else:
				text = f"\\href{{{url}}}{{{label}}}"

			yield text

	def render_children(self, token: Dict[str, Any], state: BlockState) -> str:
		children = token["children"]
		return self.render_tokens(children, state)

	def text(self, token: Dict[str, Any], state: BlockState) -> str:
		raw_text = cast(str, token["raw"])

		return to_escaped_code(raw_text)

	def emphasis(self, token: Dict[str, Any], state: BlockState) -> str:
		return "\\emph{" + self.render_children(token, state) + "}"

	def strong(self, token: Dict[str, Any], state: BlockState) -> str:
		return "\\textbf{" + self.render_children(token, state) + "}"

	def link(self, token: Dict[str, Any], state: BlockState) -> str:
		label = cast(str, token.get("label"))
		text = self.render_children(token, state)
		attrs = token["attrs"]
		url = attrs["url"]
		title = attrs.get("title")
		if title:
			return f"\\href{{{url}}}{{{text}}} \\footnote{{{title}}}"
		else:
			return f"\\href{{{url}}}{{{text}}}"

	def image(self, token: Dict[str, Any], state: BlockState) -> str:
		attrs = token["attrs"]
		src = attrs["url"]
		alt = self.render_children(token, state)
		title = attrs.get("title")

		# LaTeX format for an image
		if title:
			return f"\\begin{{figure}}\n\\centering\n\\includegraphics{{{src}}}\n\\caption{{{title}}}\n\\label{{fig:{alt}}}\n\\end{{figure}}"
		else:
			return f"\\includegraphics{{{src}}}"

	def codespan(self, token: Dict[str, Any], state: BlockState) -> str:
		code = cast(str, token["raw"])
		# Escape special LaTeX characters in the code

		# Use \texttt{} for inline code in LaTeX
		return f"\\texttt{{{to_escaped_code(code)}}}"

	def linebreak(self, token: Dict[str, Any], state: BlockState) -> str:
		return "\\\\\n % linebreak"

	def softbreak(self, token: Dict[str, Any], state: BlockState) -> str:
		return "\\\\\n % softbreak"

	def blank_line(self, token: Dict[str, Any], state: BlockState) -> str:
		return "\n"

	def inline_html(self, token: Dict[str, Any], state: BlockState) -> str:
		# return cast(str, token["raw"])
		tag_name = token["raw"].split(" ")[0][1:]
		if(tag_name not in ["answer-area", "figure"]):
			print("Unsupported inline HTML: ", token)
			return self.block_code(token, state)
		else:
			return handle_custom_tags_to_latex(token["raw"])


	def paragraph(self, token: Dict[str, Any], state: BlockState) -> str:
		text = self.render_children(token, state)
		return text + " \\newline\n"

	def heading(self, token: Dict[str, Any], state: BlockState) -> str:
		level = cast(int, token["attrs"]["level"])
		text = self.render_children(token, state)
		if level == 1:
			return f"\\section{{{text}}}\n\n"
		elif level == 2:
			return f"\\subsection{{{text}}}\n\n"
		elif level == 3:
			return f"\\subsubsection{{{text}}}\n\n"
		elif level == 4:
			return f"\\paragraph{{{text}}}\n\n"
		elif level == 5:
			return f"\\subparagraph{{{text}}}\n\n"
		else:
			return f"\\textbf{{{text}}}\n\n"

	def thematic_break(self, token: Dict[str, Any], state: BlockState) -> str:
		return "\\begin{center}\\rule{0.5\\linewidth}{0.5pt}\\end{center}\n\n"

	def block_text(self, token: Dict[str, Any], state: BlockState) -> str:
		text = self.render_children(token, state)
		return "{" + text + "}\\\\\n"

	def block_code(self, token: Dict[str, Any], state: BlockState) -> str:
		attrs = token.get("attrs", {})
		info = cast(str, attrs.get("info", ""))
		code = cast(str, token["raw"])
		if code and code[-1] != "\n":
			code += "\n"

		return f"\\begin{{verbatim}}\n{to_escaped_code(code)}\\end{{verbatim}}\n\n"

	def block_quote(self, token: Dict[str, Any], state: BlockState) -> str:
		text = self.render_children(token, state)
		return f"\\begin{{quote}}\n{text}\n\\end{{quote}}\n\n"

	def block_html(self, token: Dict[str, Any], state: BlockState) -> str:
		tag_name = token["raw"].split(" ")[0][1:]
		if(tag_name not in ["answer-area", "figure"]):
			print("Unsupported inline HTML: ", token)
			return self.block_code(token, state)
		else:
			return handle_custom_tags_to_latex(token["raw"])

	def block_error(self, token: Dict[str, Any], state: BlockState) -> str:
		return ""

	def list(self, token: Dict[str, Any], state: BlockState) -> str:
		return render_list(self, token, state)

	def table(self, token: Dict[str, Any], state: BlockState):
		return generate_latex_table(token)

	def block_math(self, token: Dict[str, Any], state: BlockState):
		return f"\n\\[\n{token["raw"]}\n\\]\n\n\n"

	def inline_math(self, token: Dict[str, Any], state: BlockState):
		return f"${token['raw']}$"


renderer = LaTeXRenderer()
latex = mistune.create_markdown(renderer=renderer, plugins=[table, math])

def markdown2latex(markdown_text: str) -> str:
    """
    Convert a markdown-formatted string to LaTeX format.

    This function takes a markdown string as input and uses the `mistune` library
    to parse and convert it into LaTeX format. The conversion is handled by a
    custom `LaTeXRenderer` which translates markdown elements (such as headings,
    links, images, etc.) into their corresponding LaTeX representations.

    Parameters:
    -----------
    markdown_text : str
        A string containing markdown-formatted text to be converted to LaTeX.

    Returns:
    --------
    str
        A string containing the LaTeX representation of the input markdown text.

    Example:
    --------
    >>> markdown_text = '''
    ... # Heading
    ... This is a **bold** text.
    ... '''
    >>> latex_output = markdown2latex(markdown_text)
    >>> print(latex_output)
    \\section{Heading}
    This is a \\textbf{bold} text. \\newline
    """
    return latex(markdown_text)
