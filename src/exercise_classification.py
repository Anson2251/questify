from utils import get_filename_with_other_ext, llm_chat
from openai import OpenAI
import json
import pathlib

def exercise_classification(exercises: list[dict], syllabus_index: list[dict], client: OpenAI, model: str) -> list[dict]:
	"""
	Classifies exercises based on the provided syllabus index using an LLM.

	Args:
		exercises (list[dict]): A list of exercise dictionaries to be classified.
		syllabus_index (list[dict]): A list of syllabus points used as a reference for classification.
		client (OpenAI): An instance of the OpenAI client for interacting with the LLM.
		model (str): The name of the LLM model to use for classification.

	Returns:
		list[dict]: A list of classified exercises, where each exercise is associated with relevant syllabus points.

		Example

		```json
		{
			"matches": [
				{
					"syllabus-id": "1.1.3",
					"relevance": 1.0
				}
			],
			"question-id": "1a"
		},
		```

	Raises:
		RuntimeError: If the LLM is not ready to process the classification request.
	"""

	prompt = pathlib.Path("prompts/classify-exercises.md").read_text()
	messages = [
		{"role": "system", "content": prompt},
		{"role": "user", "content": json.dumps({"points": syllabus_index})},
	]

	response = llm_chat(model, client, messages)
	if(json.loads(response.choices[0].message.content)["response"] != "ready"):
		raise RuntimeError("LLM not ready, please check the prompt")

	messages.append({"role": "assistant", "content": response.choices[0].message.content})
	messages.append({"role": "user", "content": json.dumps(exercises)})

	response = llm_chat(model, client, messages, True, 8192)

	return json.loads(response.choices[0].message.content)["classified"]

syllabus_index_path = "syllabus/index-9618-2021-2023-syllabus-as.json"
exercise_json_path = "papers/9618_s24_qp_13.json"

if __name__ == "__main__":
	config = json.loads(pathlib.Path("config.json").read_text())
	client = OpenAI(api_key=config["openai"]["key"], base_url=config["openai"]["base-url"])
	model = config["model"]
	syllabus = json.loads(pathlib.Path(syllabus_index_path).read_text())

	exercises = json.loads(pathlib.Path(exercise_json_path).read_text())
	syllabus = json.loads(pathlib.Path(syllabus_index_path).read_text())["points"]

	pathlib.Path("output.json").write_text(json.dumps(exercise_classification(exercises, syllabus, client, model)))


