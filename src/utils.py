
from openai import OpenAI
import os
import pathlib

def read_sql_file(path: str) -> str:
    """
    Reads the content of an SQL file from the specified path and returns it as a string.

    Args:
            path (str): The file path to the SQL file.

    Returns:
            str: The content of the SQL file as a string.
    """
    return pathlib.Path(path).read_text()

def llm_chat(model: str, client: OpenAI, messages: list[dict[str, str]], json_enabled=True, max_tokens=2048):
	"""
	Interact with an OpenAI LLM model using the chat API.

	Parameters
	----------
	model : str
		The name of the LLM model to use.
	client : OpenAI
		An OpenAI client object.
	messages : list of dict
		A list of messages to send to the LLM, in the format expected by the
		OpenAI chat API.
	json_enabled : bool, optional
		If True, the response will be in JSON format. Otherwise, it will be a
		plain string. The default is True.
	max_tokens : int, optional
		The maximum number of tokens to generate in the response. The default is
		2048.

	Returns
	-------
	dict
		The response from the LLM, in JSON format if json_enabled is True.
	"""
	return client.chat.completions.create(
		model = model,
		messages = messages,
		response_format = {"type": "json_object"} if json_enabled else None,
		stream = False,
		temperature=1,
		max_tokens=max_tokens
	)

def list_files(dir_path: str):
	"""
	List all files in a directory.

	Parameters
	----------
	dir_path : str
		The path to the directory to list the files in.

	Returns
	-------
	list of str
		A list of the paths to all the files in the given directory.
	"""
	return [os.path.join(dir_path, file) for file in os.listdir(dir_path) if (os.path.isfile(os.path.join(dir_path, file)))]

def get_filename_with_other_ext(file_name: str, extension_name: str):
	"""
	Replace the file extension of a file name with the given extension name.

	Parameters
	----------
	file_name : str
		The file name with its current extension.
	extension_name : str
		The new extension name to use.

	Returns
	-------
	str
		The file name with the new extension.
	"""
	return f"{'.'.join(file_name.split(".")[:-1])}.{extension_name}"

def get_paper_meta(file: str):
	"""
	Extract metadata from a file name based on a specific naming convention.

	The file name is expected to follow the format:
	`<syllabus_id>_<time_id>_<other_info>_<component_id>.<extension>`.

	Parameters
	----------
	file : str
		The file path or name from which to extract metadata. The file name should
		follow the expected naming convention.

	Returns
	-------
	tuple of str
		A tuple containing the extracted metadata in the following order:
		- syllabus_id (str): The syllabus identifier.
		- time_id (str): The time identifier.
		- component_id (str): The component identifier.

	Examples
	--------
	>>> get_paper_meta("123_2023_some_info_456.pdf")
	('123', '2023', '456')
	"""

	file_info = ".".join(file.split("/")[-1].split(".")[:-1]).split("_")
	syllabus_id = file_info[0]
	time_id = file_info[1]
	component_id = file_info[3]

	return (syllabus_id, time_id, component_id)

def get_paper_meta_prefix(syllabus_id, time_id, component_id):
	return f"{syllabus_id}-{time_id}-{component_id}"

def create_dir_if_not_exist(dir_path: str):
    """
    Create a directory if it does not already exist.

    Parameters
    ----------
    dir_path : str
        The path to the directory to create.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

