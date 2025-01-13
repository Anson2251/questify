CREATE TABLE exercises IF NOT EXISTS (
	id TEXT PRIMARY KEY, -- Unique identifier for the exercise
	stem TEXT NOT NULL, -- The main content of the exercise
	options TEXT, -- JSON or serialized data for options (if needed)
	figures TEXT -- JSON or serialized data for figures (if needed)
);

CREATE TABLE syllabus_points IF NOT EXISTS (
	syllabus_id TEXT PRIMARY KEY, -- Unique identifier for the syllabus point (e.g., "1.1.3")
	description TEXT -- Optional: Description of the syllabus point
);

CREATE TABLE exercise_syllabus_mapping IF NOT EXISTS (
	exercise_id TEXT, -- Foreign key to exercises.id
	syllabus_id TEXT, -- Foreign key to syllabus_points.syllabus_id
	relevance REAL, -- Relevance score (e.g., 1.0)
	PRIMARY KEY (exercise_id, syllabus_id),
	FOREIGN KEY (exercise_id) REFERENCES exercises (id),
	FOREIGN KEY (syllabus_id) REFERENCES syllabus_points (syllabus_id)
);

CREATE INDEX idx_exercise_syllabus_mapping_syllabus_id ON exercise_syllabus_mapping (syllabus_id);

CREATE INDEX idx_exercise_syllabus_mapping_exercise_id ON exercise_syllabus_mapping (exercise_id);
