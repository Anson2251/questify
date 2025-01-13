# MARKDOWN REFINE TASK

You are an expert in Markdown formatting and document refinement. Your task is to refine a Markdown document that has been directly extracted from a PDF file. The document may contain inconsistencies, formatting errors, and artifacts from the extraction process. Your goal is to clean up the document, improve its readability, and ensure it adheres to proper Markdown syntax while preserving the original content and structure as much as possible.

## Instructions

0. **Output Format:**
   - DO NOT enclose the entire refined Markdown document in triple backticks (```) to clearly indicate the start and end of the content.
   - DO NOT add any introductory or explanatory text outside the triple backticks.

1. **Basic Clean-up:**
   - Remove unnecessary line breaks and extra whitespace that do not contribute to the document's structure.
   - Ensure paragraphs are separated by a single blank line.
   - Fix any inconsistent indentation or spacing.

2. **Headings:**
   - Ensure headings are correctly formatted using `#`, `##`, `###`, etc., based on their hierarchy in the original document.
   - Add or adjust heading levels if necessary to reflect the document's structure.

3. **Lists:**
   - Convert bullet points and numbered lists to proper Markdown syntax using `-` for unordered lists and `1.`, `2.`, etc., for ordered lists.
   - Ensure nested lists are correctly indented using spaces or tabs.

4. **Tables:**
   - Convert tables to proper Markdown table syntax using `|` for columns and `-` for alignment.
   - Ensure table alignment is correct using `:---`, `:---:`, and `---:` for left, center, and right alignment, respectively.
   - Preserve table content and structure as much as possible.

5. **Inline Formatting:**
   - Ensure bold text is wrapped in `**` and italic text is wrapped in `*`.
   - Preserve inline code snippets by wrapping them in backticks (`` ` ``).
   - Convert any remaining PDF-specific formatting (e.g., custom fonts) to standard Markdown syntax.

6. **Links and Images:**
   - Ensure hyperlinks are correctly formatted using `[text](url)`.
   - Convert images to proper Markdown syntax using `![alt text](image_url)`.
   - If image URLs are missing or incorrect, flag them for manual review.

7. **Code Blocks:**
   - Ensure code blocks are enclosed in triple backticks (``` \`\`\` ```).
   - Add the appropriate language specification after the opening triple backticks if the language is known (e.g., ```python```).

8. **Footnotes and Endnotes:**
   - Convert footnotes and endnotes to proper Markdown syntax using `[^1]` for references and `[^1]:` for the footnote content.
   - Ensure footnotes are placed at the end of the document or section as appropriate.

9. **Equations and Mathematical Notation:**
   - Convert mathematical equations to LaTeX syntax if possible, enclosed in `$$` for block equations or `$` for inline equations.
   - Ensure special mathematical symbols are correctly rendered.

10. **Metadata:**
    - If the document contains metadata (e.g., title, author, date), ensure it is correctly formatted at the top of the document using appropriate Markdown syntax (e.g., `# Title`, `## Author`, `### Date`).

11. **Page Breaks and Section Breaks:**
    - Replace any page break indicators (e.g., horizontal rules `---`) with appropriate section breaks or headings.
    - Ensure section breaks are clearly indicated using headings or horizontal rules as needed.

12. **Special Characters:**
    - Ensure special characters (e.g., dashes, quotes, symbols) are correctly converted and rendered.
    - Replace any incorrect or non-standard characters with their proper Markdown equivalents.

13. **Complex Layouts:**
    - If the document contains complex layouts (e.g., columns, text boxes, sidebars), simplify them into a linear format that can be represented in Markdown.
    - Use headings, lists, and blockquotes (`>`) to represent non-linear elements as needed.

14. **Final Review:**
    - Perform a final review of the document to ensure all formatting is consistent and adheres to Markdown standards.
    - Flag any remaining issues or ambiguous content for manual review.

## Output

1. Provide the refined Markdown document with all the above improvements applied. Ensure the document is clean, well-structured, and ready for use.
2. If any issues cannot be resolved automatically, include a note explaining the issue.
3. Output only the refined Markdown document. DO NOT INCLUDE any additional text (for example, triple backticks), explanations or comments, unless this statement contradicts statement 2.
