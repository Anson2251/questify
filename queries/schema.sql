CREATE TABLE IF NOT EXISTS exercises (
	id TEXT PRIMARY KEY, -- Unique identifier for the exercise
	stem TEXT NOT NULL, -- The main content of the exercise
	options TEXT, -- JSON or serialized data for options (if needed)
	figures TEXT, -- JSON or serialized data for figures (if needed)
	origin TEXT, -- Path to the original PDF file (if applicable)
	FOREIGN KEY (origin) REFERENCES pdf_files (file_name)
);

CREATE TABLE IF NOT EXISTS syllabus_points (
	syllabus_id TEXT PRIMARY KEY, -- Unique identifier for the syllabus point (e.g., "1.1.3")
	description TEXT -- Optional: Description of the syllabus point
);

CREATE TABLE IF NOT EXISTS exercise_syllabus_mapping (
	exercise_id TEXT, -- Foreign key to exercises.id
	syllabus_id TEXT, -- Foreign key to syllabus_points.syllabus_id
	relevance REAL, -- Relevance score (e.g., 1.0)
	PRIMARY KEY (exercise_id, syllabus_id),
	FOREIGN KEY (exercise_id) REFERENCES exercises (id),
	FOREIGN KEY (syllabus_id) REFERENCES syllabus_points (syllabus_id)
);

CREATE TABLE IF NOT EXISTS pdf_files (
	file_name TEXT PRIMARY KEY, -- Name of the PDF file
	file_data BLOB NOT NULL -- Binary data of the PDF file
);

CREATE INDEX IF NOT EXISTS idx_exercise_syllabus_mapping_syllabus_id ON exercise_syllabus_mapping (syllabus_id);

CREATE INDEX IF NOT EXISTS idx_exercise_syllabus_mapping_exercise_id ON exercise_syllabus_mapping (exercise_id);

CREATE INDEX IF NOT EXISTS idx_pdf_files_file_name ON pdf_files (file_name);
