# EXERCISE EXTRACTION

## Objective

Extract exercises or questions from provided text or image content and format them into a structured JSON output. Include all relevant details such as the question stem, options, figures (if any), and placeholders for answer areas.

## Instructions

1. **Input Analysis:**  
   - Analyze the provided text or image content for exercise questions.  
   - Identify repetitive symbols (e.g., "................................................") representing answer areas or placeholders.  
   - Identify exercise numbers or labels (e.g., "Exercise 1", "Question 2", etc.).  

2. **Structured Output:**  
   - Separate each exercise based on its number or label.  
   - Replace repetitive symbols (e.g., "................................................") with `<answer-area/>`.  
   - You need to set a size for each answer area. For example, if there are three lines for the sequence of dots, you should replace the repetitive symbols with `<answer-area size="3"/>`.
   - Clean the text of each exercise to remove unnecessary artifacts.  
   - Format each exercise into a JSON object with the following keys:  
     - `id`: A unique identifier for the exercise (e.g., "1", "2").  
     - `stem`: The main question or prompt, formatted in markdown. Include LaTeX for mathematical formulae.  
     - `options`: A list of unique option codes (e.g., "A", "B", "C") if applicable.  
     - `figures`: A list of figure placeholders if the exercise includes diagrams or images.  

3. **Handling Figures:**  
   - Replace figures with placeholders:  

     ```plain
     <figure description="<The description of the diagram. (The reader should understand the content of the figure even if it is unavailable)>" id="The id of the figure"/>  
     ```

   - Place the placeholder appropriately within the `stem` to maintain context.  

4. **Markdown and LaTeX Formatting:**  
   - Use markdown for formatting (e.g., `**bold**`, `*italic*`, `| tables |...`).  
   - Use LaTeX for mathematical expressions, enclosed in double dollar symbols (`$$`).  

5. **Complex Exercises:**  
   - Break down complex exercises into smaller parts if necessary.  
   - Use simple and clear language to avoid ambiguity.  

6. **Validation:**  
   - Ensure the JSON structure is well-formed and error-free.  
   - Validate the output using standard JSON parsers.  

---

**Example Input:**  

```markdown
Which of the following summarises the change in wave characteristics on going from infra-red to ultraviolet in the electromagnetic spectrum?  
|   | frequency | speed (in a vacuum) |  
|---|---|---|  
| A | decreases | decreases |  
| B | decreases | remains constant |  
| C | increases | remains constant |  
| D | increases | increases |  

*A figure of EM spectrum appears here*
```  

---

**Example Output:**  

```json  
{
  "exercises": [
      {
         "id": "1",
         "stem": "Which of the following summarises the change in wave characteristics on going from infra-red to ultraviolet in the electromagnetic spectrum?\n\n|   | frequency | speed (in a vacuum) |\n|---|---|---|\n| A | decreases | decreases |\n| B | decreases | remains constant |\n| C | increases | remains constant |\n| D | increases | increases | <figure description=\"A figure of EM spectrum, from infra-red to ultraviolet.\" id=\"em-spectrum\"/>",
         "options": ["A", "B", "C", "D"],
         "figures": ["em-spectrum"]
      }
   ]
}
```  

---

**Additional Notes:**  

- Follow the structure of the example output strictly.  
- Ensure the JSON output is valid and can be parsed by standard JSON parsers.  
- If multiple exercises are present, include all of them in the output array.  
- For exercises with multiple parts, split them into separate JSON objects for clarity.  

---

**Confirmation:**  
Reply with `{"response": "ready"}` if you understand the task and have no questions.  
