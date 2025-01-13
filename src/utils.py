
from openai import OpenAI
import os

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