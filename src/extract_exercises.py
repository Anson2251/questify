import pymupdf4llm
from openai import OpenAI
from zhipuai import ZhipuAI
import pathlib
import json
import tqdm

from utils import llm_chat, list_files, get_filename_with_other_ext


def extract_exercises_to_json(paper_md_text: str, client: OpenAI, model: str):
	"""
	Extracts exercises from a PDF file and returns them as a JSON object.

	Args:
		pdf_path (str): The path to the PDF file from which exercises are to be extracted.
		client (OpenAI): The OpenAI client used to interact with the LLM.
		model (str): The model name to be used for the LLM.

	Returns:
		list: A list of dictionaries, where each dictionary represents an exercise with the following keys:

			- id (str): The unique identifier for the exercise.
			- stem (str): The question or problem statement.
			- options (list): A list of possible answers or choices.
			- figures (list): A list of figures or images associated with the exercise.

	Raises:
		RuntimeError: If the LLM is not ready or if the response from the LLM is not a valid JSON.
	"""

	classification_prompt = pathlib.Path("prompts/extraction-prompt.md").read_text()
	pre_content_prompt = pathlib.Path("prompts/extraction-pre-content-prompt.md").read_text()

	pathlib.Path(get_filename_with_other_ext(file, "md")).write_text(paper_md_text)

	# model = "deepseek-chat"
	# model = "glm-4-flash"

	messages = [
		{"role": "system", "content": classification_prompt},
		{"role": "user", "content": "Are you ready to begin?"},
	]

	response = llm_chat(model, client, messages)
	if(json.loads(response.choices[0].message.content)["response"] != "ready"):
		raise RuntimeError("LLM not ready, please check the prompt")

	messages.append({"role": "assistant", "content": response.choices[0].message.content})
	messages.append({"role": "user", "content": f"{pre_content_prompt}\n\n{paper_md_text}"})

	retry_times = 0
	exit_flag = False
	extracted_exercises = []
	while not exit_flag and retry_times < 5:
		response = llm_chat(model, client, messages, max_tokens=8192)
		messages.append({"role": "assistant", "content": response.choices[0].message.content})

		try:
			extracted = json.loads(response.choices[0].message.content)
		except(json.JSONDecodeError):
			raise RuntimeError("LLM response is not a valid JSON, check the max_tokens parameter.")

		# If the extracted JSON does not contain the 'exercises' key, ask the LLM to check again
		if "exercises" not in extracted:
			print("The extracted JSON does not contain the 'exercises' key. Asking the LLM to check again.")
			messages.append({"role": "user", "content": f"The extracted JSON does not contain the 'exercises' key. Please check the prompt and try again."})
			retry_times += 1
			continue

		exercises = extracted["exercises"]

		# If the number of exercises is too small, ask the LLM to check again
		if ((len(exercises) < 5) and (retry_times == 0)):
			print("The number of exercises is too small. Asking the LLM to check again.")
			messages.append({"role": "user", "content": f"Are you sure that you have extracted all the exercises? Please check again. \nIf everything works fine, please return the same JSON again. Otherwise, please extract again."})
			retry_times += 1
			continue

		exercise_valid_flag = True
		for exercise in exercises:
			if(set(exercise.keys()) != set(["id", "stem",  "options", "figures"])):
				print("The extracted JSON does not contain the correct keys. Asking the LLM to check again.")
				messages.append({"role": "user", "content": f"The extracted JSON does not contain the correct keys. Please check the prompt and try again."})
				exercise_valid_flag = False
				break
			if(not isinstance(exercise["stem"], str)):
				print("The extracted JSON does not contain the correct stem. Asking the LLM to check again.")
				messages.append({"role": "user", "content": f"The extracted JSON does not contain the correct stem. Please check the prompt and try again."})
				exercise_valid_flag = False
				break

		if(not exercise_valid_flag):
			retry_times += 1
			continue

		exit_flag = True
		extracted_exercises = extracted["exercises"]

	return extracted_exercises

def batch_extract_to_json(pdf_paths: list[str], client, model: str):
	return [{"file": pdf_path, "json": extract_exercises_to_json(pdf_path, client, model)} for pdf_path in tqdm.tqdm(pdf_paths)]

if __name__ == "__main__":
	config = json.loads(pathlib.Path("config.json").read_text())
	client = OpenAI(api_key=config["openai"]["key"], base_url=config["openai"]["base-url"])
	# client = ZhipuAI(api_key=config["zhipuai"]["key"])

	pdf_folder = "papers"
	model = config["model"]

	files = [file for file in list_files(pdf_folder) if file.endswith(".pdf")]
	progress_bar = tqdm.tqdm(files)

	for file in files:
		text = pymupdf4llm.to_markdown(file, show_progress=False)
		extracted = extract_exercises_to_json(text, client, model)
		pathlib.Path(get_filename_with_other_ext(file, "json")).write_text(json.dumps(extracted, indent=2, ensure_ascii=False))
		progress_bar.update(1)
