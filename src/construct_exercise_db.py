import sqlite3
from sqlite3 import Connection
import pathlib
from utils import list_files, get_filename_with_other_ext
from exercise_classification import exercise_classification
from openai import OpenAI
import json
from tqdm import tqdm


def prepare_table(cursor: Connection):
    schema = read_sql_file("queries/schema.sql")
    cursor.executescript(schema)


def read_sql_file(path: str) -> str:
    """
    Reads the content of an SQL file from the specified path and returns it as a string.

    Args:
            path (str): The file path to the SQL file.

    Returns:
            str: The content of the SQL file as a string.
    """
    return pathlib.Path(path).read_text()


def insert_exercise(cursor: Connection, exercise: dict):
    cursor.execute("BEGIN TRANSACTION")
    query = read_sql_file("queries/insert-exercise.sql")

    try:
        cursor.execute(
            query,
            (
                exercise["id"],
                exercise["stem"],
                json.dumps(exercise["options"]),
                json.dumps(exercise["figures"]),
                exercise["origin"],
            ),
        )
    except Exception as e:
        cursor.execute("ROLLBACK")
        print("Fail to insert exercise due to", e)
        raise RuntimeError("Failed to insert exercise")
    cursor.execute("COMMIT")


def insert_syllabus(cursor: Connection, syllabus: list[dict]):
    cursor.execute("BEGIN TRANSACTION")
    query = read_sql_file("queries/insert-syllabus-points.sql")

    for point in syllabus:
        try:
            cursor.execute(query, (point["id"], point["description"]))
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Fail to insert syllabus point due to", e)
            raise RuntimeError("Failed to insert syllabus point")
    cursor.execute("COMMIT")


def insert_matching(cursor: Connection, matching: list[dict]):
    # exercise_id, syllabus_id, relevance
    cursor.execute("BEGIN TRANSACTION")
    query = read_sql_file("queries/insert-exercise-syllabus-mapping.sql")

    for match in matching:
        try:
            cursor.execute(
                query, (match["question-id"], match["syllabus-id"], match["relevance"])
            )
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Fail to insert matching due to", e)
            raise RuntimeError("Failed to insert matching")
    cursor.execute("COMMIT")


def insert_pdf_file(cursor: Connection, file_path: str, file_name: str = None):
    if file_name == None:
        file_name = pathlib.Path(file_path).name
    cursor.execute("BEGIN TRANSACTION")
    query = read_sql_file("queries/insert-pdf-file.sql")

    try:
        with open(file_path, "rb") as file:
            file_data = file.read()

        cursor.execute(query, (file_name, file_data))
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")
        raise RuntimeError("Failed to insert pdf file " + file_path)
    cursor.execute("COMMIT")


if __name__ == "__main__":
    # exercises_folder = "paper"
    # files = [file for file in list_files(exercises_folder) if file.endswith(".json")]

    config = json.loads(pathlib.Path("config.json").read_text())
    client = OpenAI(
        api_key=config["openai"]["key"], base_url=config["openai"]["base-url"]
    )
    model = config["model"]

    syllabus = json.loads(
        pathlib.Path("syllabus/index-9618-2021-2023-syllabus-as.json").read_text()
    )
    files = [file for file in list_files("papers") if file.endswith(".json")]

    cursor = sqlite3.connect("./papers.db")
    prepare_table(cursor)
    insert_syllabus(cursor, syllabus["points"])

    for file in tqdm(files):
        original_pdf_file = get_filename_with_other_ext(file, "pdf")
        insert_pdf_file(cursor, original_pdf_file)

        exercises = [
            {**e, **{"matching_syllabus": None, "origin": pathlib.Path(original_pdf_file).name}}
            for e in json.loads(pathlib.Path(file).read_text())
        ]

        classification = exercise_classification(exercises, syllabus, client, model)
        for exercise in exercises:
            info_in_matching = list(
                filter(lambda x: x["question-id"] == exercise["id"], classification)
            )
            if len(info_in_matching) == 0:
                print("Warning: Fail to find matching for exercise: " + exercise["id"])
                continue
            exercise["matching_syllabus"] = info_in_matching[0]["matches"]

        for exercise in exercises:
            try:
                insert_exercise(cursor, exercise)
            except:
                print("Warning: Fail to insert exercise: " + exercise["id"])

        matchings = []
        for exercise in exercises:
            if exercise["matching_syllabus"] == None:
                continue
            for match in exercise["matching_syllabus"]:
                matchings.append(
                    {
                        "syllabus-id": match["syllabus-id"],
                        "question-id": exercise["id"],
                        "relevance": match["relevance"],
                    }
                )

        insert_matching(cursor, matchings)
