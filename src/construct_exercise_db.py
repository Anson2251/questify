import sqlite3
from sqlite3 import Connection
import pathlib
from utils import list_files, get_filename_with_other_ext, read_sql_file
from exercise_classification import exercise_classification
from openai import OpenAI
import json
from tqdm import tqdm


def prepare_table(connection: Connection):
    schema = read_sql_file("src/queries/schema.sql")
    connection.executescript(schema)


def insert_exercise(connection: Connection, exercise: dict):
    connection.execute("BEGIN TRANSACTION")
    query = read_sql_file("src/queries/insert-exercise.sql")

    try:
        connection.execute(
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
        connection.execute("ROLLBACK")
        print("Fail to insert exercise due to", e)
        raise RuntimeError("Failed to insert exercise")
    connection.execute("COMMIT")


def insert_syllabus(connection: Connection, syllabus: list[dict]):
    connection.execute("BEGIN TRANSACTION")
    query = read_sql_file("src/queries/insert-syllabus-points.sql")

    for point in syllabus:
        try:
            connection.execute(query, (point["id"], point["description"]))
        except Exception as e:
            connection.execute("ROLLBACK")
            print("Fail to insert syllabus point due to", e)
            raise RuntimeError("Failed to insert syllabus point")
    connection.execute("COMMIT")


def insert_matching(connection: Connection, matching: list[dict]):
    # exercise_id, syllabus_id, relevance
    connection.execute("BEGIN TRANSACTION")
    query = read_sql_file("src/queries/insert-exercise-syllabus-mapping.sql")

    for match in matching:
        try:
            connection.execute(
                query, (match["question-id"], match["syllabus-id"], match["relevance"])
            )
        except Exception as e:
            connection.execute("ROLLBACK")
            print("Fail to insert matching due to", e)
            raise RuntimeError("Failed to insert matching")
    connection.execute("COMMIT")


def insert_pdf_file(connection: Connection, file_path: str, file_name: str = None):
    if file_name == None:
        file_name = pathlib.Path(file_path).name
    connection.execute("BEGIN TRANSACTION")
    query = read_sql_file("src/queries/insert-pdf-file.sql")

    try:
        with open(file_path, "rb") as file:
            file_data = file.read()

        connection.execute(query, (file_name, file_data))
    except sqlite3.Error as e:
        connection.execute("ROLLBACK")
        raise RuntimeError("Failed to insert pdf file " + file_path)
    connection.execute("COMMIT")


if __name__ == "__main__":
    # exercises_folder = "paper"
    # files = [file for file in list_files(exercises_folder) if file.endswith(".json")]

    config = json.loads(pathlib.Path("config.json").read_text())
    client = OpenAI(
        api_key=config["openai"]["key"], base_url=config["openai"]["base-url"]
    )
    model = config["model"]

    syllabus = json.loads(pathlib.Path("syllabus/index-9618-2021-2023-syllabus-as.json").read_text())
    files = [file for file in list_files("papers") if file.endswith(".json")]

    connection = sqlite3.connect("./papers.db")
    prepare_table(connection)
    insert_syllabus(connection, syllabus["points"])

    for file in tqdm(files):
        original_pdf_file = get_filename_with_other_ext(file, "pdf")
        insert_pdf_file(connection, original_pdf_file)

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
                insert_exercise(connection, exercise)
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

        insert_matching(connection, matchings)
