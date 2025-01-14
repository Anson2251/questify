SELECT
	e.id,
	e.stem,
	esm.relevance
FROM
	exercises e
	JOIN exercise_syllabus_mapping esm ON e.id = esm.exercise_id
WHERE
	(esm.syllabus_id LIKE ?)
	AND (esm.relevance >= ?)
ORDER BY
	esm.relevance DESC;
