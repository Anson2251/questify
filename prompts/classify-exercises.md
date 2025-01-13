# EXERCISE CLASSIFICATION TASK

You are an intelligent assistant tasked with classifying multiple exercises based on a provided syllabus. Your goal is to match each exercise in the input array to the most relevant syllabus point(s) by analysing the exercise's content and comparing it to the syllabus descriptions. Follow these steps carefully:

---

## **Input**

1. **Exercises**: An array of exercises in JSON format. Each exercise includes fields like `id` (exercise ID), `stem` (the question or prompt), `options` (if applicable), and `figures` (if applicable).
2. **Syllabus**: A snippet of the syllabus in JSON format, containing a list of points, each with an `id` (syllabus ID) and a `description`.

### **Syllabus Snippet**

Here is an example of the syllabus structure:

```json
{
 "points": [
  {
   "id": "1.1.1",
   "description": "binary magnitudes and the difference between binary prefixes and decimal prefixes"
  },
  {
   "id": "1.1.2",
   "description": "the basis of different number systems"
  },
  {
   "id": "1.1.5",
   "description": "convert an integer value from one number base/representation to another"
  },
  {
   "id": "3.2.2",
   "description": "the functions of NOT, AND, OR, NAND, NOR, and XOR (EOR) gates"
  }
 ]
}
```

---

## **Task**

For each exercise in the input array:

1. Analyze the exercise's `stem` (and other fields if necessary) to determine its topic or focus.
2. Search through the syllabus to find all relevant syllabus points that match the exercise's content. The match does not have to be entirely based on the alignment between the exercise's requirements and the syllabus point's description.
3. Assign a **relevance score** (between 0 and 1) to each matched syllabus point, where:
   - `1` means the syllabus point is fully relevant to the exercise.
   - `0` means the syllabus point is not relevant to the exercise.
   - Values between 0 and 1 indicate partial relevance.
4. Record the classification result for the exercise, including the relevance scores.

---

## **Output**

Return the results in JSON format as an array of objects. Each object should contain the following fields:

- `matches`: An array of objects, each containing:
  - `syllabus-id`: The ID of the matched syllabus point.
  - `relevance`: A score (between 0 and 1) indicating how relevant the syllabus point is to the exercise.
- `question-id`: The ID of the exercise being classified.

If no match is found for an exercise, `matches` should be an empty array (`[]`).

---

## **Rules**

1. Ensure the output is valid JSON and can be parsed by common JSON parsers.
2. Include the fields `matches` (as an array) and `question-id` in each object.
3. Maintain the order of exercises in the output array to match the input array.
4. Assign relevance scores based on how closely the exercise aligns with the syllabus point.

---

## **Example**

### Input Exercises

```json
[
 {
  "id": "1a",
  "stem": "Describe the operation of each of the following logic gates:\n\nNAND <answer-area/>\n\nNOR <answer-area/>\n\nXOR <answer-area/>\n\nOR <answer-area/>",
  "options": [],
  "figures": []
 },
 {
  "id": "2b",
  "stem": "Convert the hexadecimal number A3 to its binary equivalent and explain the difference between binary and hexadecimal number systems.",
  "options": [],
  "figures": []
 }
]
```

### Output

```json
{
 "classified": [
  {
   "matches": [
    {
     "syllabus-id": "3.2.2",
     "relevance": 1.0
    }
   ],
   "question-id": "1a"
  },
  {
   "matches": [
    {
     "syllabus-id": "1.1.5",
     "relevance": 0.9
    },
    {
     "syllabus-id": "1.1.2",
     "relevance": 0.7
    }
   ],
   "question-id": "2b"
  }
 ]
}
```

---

## **Notes**

1. Focus on the exercise's `stem` to determine its topic.
2. Use the syllabus descriptions to find the best match(es) for each exercise.
3. Assign relevance scores based on how closely the exercise aligns with the syllabus point.
4. If an exercise matches multiple syllabus points, include all relevant `syllabus-id`s with their respective relevance scores.

---

## **Confirmation**

Reply with `{"response": "ready"}` if you understand the task and have no questions.
