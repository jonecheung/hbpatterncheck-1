# HB Pattern Chatbot - Usage Examples

Practical examples of how to use the chatbot effectively.

## Getting Started

### Launch the chatbot:
```bash
streamlit run src/5_app.py
```

Access at: http://localhost:8501

---

## Text Query Examples

### 1. Disease Characteristics

**Query:**
```
What are the characteristics of HbE disease?
```

**What it does:**
- Searches for HbE disease mentions
- Retrieves relevant patient cases
- Provides summary with source citations

**Expected response:**
- Clinical features
- Chromatograph patterns
- Page references

---

### 2. Pattern Identification

**Query:**
```
Show cases with elevated HbA2 levels
```

**What it does:**
- Finds cases mentioning HbA2
- Identifies elevation patterns
- Shows similar chromatographs

**Expected response:**
- Patient cases with elevated HbA2
- Normal vs. abnormal ranges
- Associated conditions

---

### 3. Diagnostic Indicators

**Query:**
```
What retention times indicate beta thalassemia?
```

**What it does:**
- Searches for beta thalassemia
- Finds retention time data
- Explains diagnostic criteria

**Expected response:**
- Specific retention time ranges
- Peak patterns
- Diagnostic interpretation

---

### 4. Pattern Comparison

**Query:**
```
Find patterns similar to HbH disease
```

**What it does:**
- Identifies HbH characteristics
- Searches for similar patterns
- Provides comparative analysis

**Expected response:**
- Cases with similar patterns
- Pattern variations
- Differential diagnosis

---

## Image Query Examples

### 1. Visual Pattern Search

**Steps:**
1. Click "Upload Chromatograph Image"
2. Select an image file
3. Click "Search by image"

**What it does:**
- GPT-4V analyzes the image
- Generates technical description
- Finds visually similar patterns

**Expected response:**
- Similar chromatograph patterns
- Matching patient cases
- Pattern characteristics

---

### 2. Combined Text + Image

**Steps:**
1. Upload chromatograph image
2. Enter query: "What disease shows this pattern?"

**What it does:**
- Analyzes uploaded image
- Combines with text query
- Provides comprehensive answer

**Expected response:**
- Disease identification
- Pattern explanation
- Supporting cases

---

## Advanced Queries

### 1. Multi-criteria Search

**Query:**
```
Find cases with both elevated HbA2 and abnormal HbF levels
```

**What it does:**
- Searches for multiple criteria
- Finds cases matching all conditions
- Prioritizes best matches

---

### 2. Quantitative Analysis

**Query:**
```
What are normal ranges for HbA2 percentage?
```

**What it does:**
- Searches for quantitative data
- Extracts numerical ranges
- Provides reference values

---

### 3. Differential Diagnosis

**Query:**
```
How to differentiate between HbE trait and beta thalassemia minor?
```

**What it does:**
- Finds both conditions
- Compares characteristics
- Highlights differences

---

## Using Sidebar Settings

### Number of Results

**Slider: 1-10 (default: 5)**

- **Low (1-3):** Fast, focused results
- **Medium (4-6):** Balanced
- **High (7-10):** Comprehensive, slower

**When to adjust:**
- Need specific info → Lower
- Exploratory search → Higher

---

### Show Sources

**Toggle: On/Off**

- **On:** See page references and similarity scores
- **Off:** Cleaner chat interface

**When to use:**
- Research/verification → On
- Quick lookup → Off

---

### Search Mode

**Options:**
1. **Text only:** Fast, text-based search
2. **Image upload:** Visual pattern matching
3. **Both:** Multimodal search

**When to use each:**
- General questions → Text only
- Pattern recognition → Image upload
- Complex diagnosis → Both

---

## Tips for Better Results

### 1. Be Specific

❌ **Bad:** "Tell me about hemoglobin"
✅ **Good:** "What are the characteristics of HbS trait?"

### 2. Use Medical Terms

❌ **Bad:** "Blood problem patterns"
✅ **Good:** "Beta thalassemia chromatograph patterns"

### 3. Ask Focused Questions

❌ **Bad:** "Everything about hemoglobin diseases"
✅ **Good:** "What causes elevated HbF in adults?"

### 4. Reference Specifics

✅ **Good examples:**
- "Peak at 3.2 minutes retention time"
- "HbA2 percentage above 3.5%"
- "Abnormal peak patterns in zone 2"

---

## Sample Conversation Flow

### Example 1: Diagnosing a Pattern

**User:** "What are signs of HbH disease?"

**Bot:** [Provides characteristics with page references]

**User:** [Uploads chromatograph]

**Bot:** [Analyzes image and finds similar cases]

**User:** "How certain is this diagnosis?"

**Bot:** [Explains confidence based on pattern match and retrieved cases]

---

### Example 2: Learning About a Condition

**User:** "What is beta thalassemia minor?"

**Bot:** [Provides definition and characteristics]

**User:** "Show me example chromatographs"

**Bot:** [Lists cases with image references]

**User:** "What are typical HbA2 levels?"

**Bot:** [Provides quantitative information]

---

## Interpreting Results

### Similarity Scores

- **90-100%:** Highly relevant
- **70-89%:** Relevant
- **50-69%:** Somewhat relevant
- **<50%:** May not be directly relevant

### Source Citations

Format: `[1] Page 23 (Image: page_23_img_0.png)`

- **[1], [2], etc.:** Source number
- **Page X:** PDF page number
- **Image:** If from chromatograph description
- **Text:** If from text content

---

## Common Use Cases

### 1. Student Learning

"Explain the differences between HbS and HbC patterns"

### 2. Case Review

Upload patient chromatograph → "Find similar cases"

### 3. Reference Lookup

"What are normal HbA2 ranges?"

### 4. Pattern Recognition

"Identify this unusual peak pattern" + image

### 5. Differential Diagnosis

"Compare HbE disease vs HbE trait chromatographs"

---

## Keyboard Shortcuts

- **Enter:** Send message
- **Shift+Enter:** New line in message
- **Esc:** Clear input field

---

## Best Practices

### ✅ Do:
- Ask specific medical questions
- Use standard terminology
- Upload clear chromatograph images
- Check source citations
- Verify critical information

### ❌ Don't:
- Use for clinical diagnosis without verification
- Expect answers outside the database
- Upload low-quality images
- Ignore source references
- Use without understanding limitations

---

## Limitations

1. **Database scope:** Only knows information in the PDF
2. **Not a diagnostic tool:** Requires professional interpretation
3. **Image quality:** Better images → better matches
4. **Context:** May miss context from outside the database
5. **Updates:** Database must be manually updated

---

## Feedback Loop

To improve results:

1. **Refine queries** if results are off-target
2. **Adjust k-value** (number of results) in sidebar
3. **Try different phrasings** for the same question
4. **Use both text and image** for complex cases
5. **Check sources** to verify relevance

---

## Example Sessions

### Session 1: Quick Lookup
```
Q: Normal HbA2 range?
A: [Quick answer with percentages]
✅ Fast, focused
```

### Session 2: Deep Dive
```
Q: Tell me about HbE disease
A: [Comprehensive overview]
Q: Show similar patterns
A: [Lists cases]
Q: [Uploads image]
A: [Matches pattern]
✅ Thorough investigation
```

### Session 3: Comparison
```
Q: Compare HbS trait vs HbS disease
A: [Detailed comparison]
Q: What are treatment differences?
A: [Treatment information if available]
✅ Comparative analysis
```

---

**Happy searching! 🔬**

