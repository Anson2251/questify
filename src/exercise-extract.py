import pymupdf4llm
from openai import OpenAI
from zhipuai import ZhipuAI
import pathlib
import json
import tqdm
import os

from utils import llm_json_chat, list_files, get_filename_with_other_ext


def extract_to_json(pdf_path: str, client: OpenAI, model: str, classification_prompt: str, pre_content_prompt: str, quiet: bool = False):
	paper_md_text = pymupdf4llm.to_markdown(pdf_path, show_progress=not quiet)
	pathlib.Path(get_filename_with_other_ext(file, "md")).write_text(paper_md_text)

	# model = "deepseek-chat"
	# model = "glm-4-flash"
	
	messages = [
		{"role": "system", "content": classification_prompt},
		{"role": "user", "content": "Are you ready to begin?"},
	]

	if(not quiet): print("Extracting exercises...")
	response = llm_json_chat(model, client, messages)
	if(json.loads(response.choices[0].message.content)["response"] != "ready"):
		raise RuntimeError("LLM not ready, please check the prompt")

	if(not quiet): print(f'LLM status: {json.loads(response.choices[0].message.content)["response"]}')
	messages.append({"role": "assistant", "content": response.choices[0].message.content})

	messages.append({"role": "user", "content": f"{pre_content_prompt}\n\n{paper_md_text}"})
	response = llm_json_chat(model, client, messages)

	return response.choices[0].message.content

def batch_extract_to_json(pdf_paths: list[str], client, model: str, classification_prompt: str, pre_content_prompt: str):
	return [{"file": pdf_path, "json": extract_to_json(pdf_path, client, model, classification_prompt, pre_content_prompt, True)} for pdf_path in tqdm.tqdm(pdf_paths)]

if __name__ == "__main__":
	config = json.loads(pathlib.Path("config.json").read_text())
	client = OpenAI(api_key=config["openai"]["key"], base_url=config["openai"]["base-url"])
	# client = ZhipuAI(api_key=config["zhipuai"]["key"])
	classification_prompt = pathlib.Path("prompts/extraction-prompt.md").read_text()
	extract_pre_content_prompt = pathlib.Path("prompts/extraction-pre-content-prompt.md").read_text()
	pdf_folder = "papers"
	model = config["model"]

	files = [file for file in list_files(pdf_folder) if file.endswith(".pdf")]
	progress_bar = tqdm.tqdm(files)

	for file in files:
		extracted = extract_to_json(file, client, model, classification_prompt, extract_pre_content_prompt, True)
		retry_time = 0
		pathlib.Path(get_filename_with_other_ext(file, "json")).write_text(extracted)
		while (len(json.loads(extracted)["exercises"]) < 5) and retry_time < 5:
			retry_time += 1
			print("Warning: The number of exercises extracted is to little. retrying")
			extracted = extract_to_json(file, client, model, classification_prompt, extract_pre_content_prompt, True)
			pathlib.Path(get_filename_with_other_ext(file, "json")).write_text(extracted)
		progress_bar.update(1)

