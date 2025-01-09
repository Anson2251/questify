
from openai import OpenAI
import os

def llm_json_chat(model: str, client: OpenAI, messages: list[dict[str, str]], json_enabled=True, max_tokens=2048):
	return client.chat.completions.create(
		model = model,
		messages = messages,
		response_format = {"type": "json_object"} if json_enabled else None,
		stream = False,
		temperature=1,
		max_tokens=max_tokens
	)

def list_files(dir_path: str):
	return [os.path.join(dir_path, file) for file in os.listdir(dir_path) if (os.path.isfile(os.path.join(dir_path, file)))]

def get_filename_with_other_ext(file_name: str, extension_name: str):
	return "".join((file_name.split(".")[:-1])) + f".{extension_name}"