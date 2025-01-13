from utils import get_filename_with_other_ext, llm_chat
from openai import OpenAI
import json
import pathlib

def syllabus_index_construction(syllabus_text: str, client: OpenAI, model: str):
	"""
	Constructs an index for the given syllabus text using an LLM (Language Learning Model).

	Args:
		syllabus_text (str): The text content of the syllabus.
		client (OpenAI): An instance of the OpenAI client used to interact with the LLM.
		model (str): The name of the LLM model to be used for generating the index.

	Returns:
		str: The generated index content as a string.
	"""

	prompt = pathlib.Path("prompts/syllabus-index.md").read_text()
	messages = [
		{"role": "system", "content": prompt},
		{"role": "user", "content": syllabus_text},
	]
	return llm_chat(model, client, messages, True, 8192).choices[0].message.content

syllabus_md_path = "syllabus/9618-2021-2023-syllabus-as.md"

if __name__ == "__main__":
	config = json.loads(pathlib.Path("config.json").read_text())
	client = OpenAI(api_key=config["openai"]["key"], base_url=config["openai"]["base-url"])
	model = config["model"]
	syllabus_text = pathlib.Path(syllabus_md_path).read_text()
	index_path = "/".join(syllabus_md_path.split("/")[:-1] + ["index-" + get_filename_with_other_ext(syllabus_md_path, "json").split("/")[-1]])
	pathlib.Path(index_path).write_text(syllabus_index_construction(syllabus_text, client, model))
