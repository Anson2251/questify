import pymupdf4llm
import pathlib
import json
import os
from openai import OpenAI

from utils import llm_json_chat, list_files, get_filename_with_other_ext

def to_markdown(pdf_path):
    return pymupdf4llm.to_markdown(pdf_path, show_progress=False)

def llm_markdown_refine(text: str, client: OpenAI, model: str):
    prompt = pathlib.Path("prompts/refine-markdown.md").read_text()
    messages = [
		{"role": "system", "content": prompt},
		{"role": "user", "content": text},
	]
    return llm_json_chat(model, client, messages, False, 8192).choices[0].message.content

if __name__ == "__main__":
    config = json.loads(pathlib.Path("config.json").read_text())
    client = OpenAI(api_key=config["openai"]["key"], base_url=config["openai"]["base-url"])
    model = config["model"]

    syllabuses = [file for file in list_files("syllabus") if file.endswith(".pdf")]
    for syllabus in syllabuses:
        md_name = get_filename_with_other_ext(syllabus, "md")
        if(os.path.exists(md_name)): os.remove(md_name)
        pathlib.Path(md_name).write_text(llm_markdown_refine(to_markdown(syllabus), client, model))

