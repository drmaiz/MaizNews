# Token Optimization Guide for Daily Briefings

## Understanding Token Usage

In Claude, approximately:
- **1 token ≈ 4 characters** or **1 word = 1.3 tokens**
- A typical 1000-word briefing = ~1,300 tokens
- System prompt = ~300-400 tokens

**Goal**: Create a rich, informative briefing in under 1,500 tokens total (including system prompt).

---

## Token-Saving Techniques

### 1. **Writing Style**
| ❌ Inefficient | ✅ Efficient | Tokens Saved |
|---|---|---|
| "The company announced that it would be" | "The company will" | 60% |
| "In a groundbreaking development" | "Breaking:" | 70% |
| "According to reports from the source" | "Source says" | 65% |
| "This is important because" | "Impact:" | 50% |

### 2. **Abbreviation Strategy**
Use these abbreviations liberally:

**Standard**
- govt (government)
- yr/yrs (year/years)
- mo/mos (month/months)
- w/ (with)
- & (and)
- vs (versus)
- max/min (maximum/minimum)
- approx (approximately)
- incl (including)
- excl (excluding)

**Tech/Finance**
- AI (artificial intelligence)
- ML (machine learning)
- API (application programming interface)
- IPO (initial public offering)
- M&A (mergers & acquisitions)
- GDP (gross domestic product)
- Q1/Q2 (quarters)
- YoY (year-over-year)
- AUM (assets under management)

**Region Abbreviations** (use only when context is clear)
- US (United States)
- EU (European Union)
- UK (United Kingdom)
- HQ (headquarters)

### 3. **Structure Optimization**

❌ **Before** (78 tokens):
"The new AI model was announced today by OpenAI. The model, which has been developed over the past year, offers significant improvements in reasoning capabilities. The company said that it will be available to users starting next week."

✅ **After** (42 tokens):
"OpenAI announced GPT-5 with improved reasoning. Available next week."

**Reduction: 46% fewer tokens**

### 4. **Category Use Instead of Descriptions**
Instead of explaining the category:
- ❌ "This is about artificial intelligence and technology" (9 tokens)
- ✅ "🟢 TECH" (2 tokens + emoji)

**Savings: 78%**

### 5. **Structured Summary Format**

Use format: `[What] • [Why it matters] • [Next]`

**Example:**
"OpenAI launches GPT-5 • 40% fewer hallucinations • API access starts June 20"

This replaces paragraph text and saves ~30-40% tokens while maintaining clarity.

### 6. **Metadata Compression**

❌ Full format:
"This news comes from the Reuters news agency and was published approximately 2 hours ago"

✅ Compressed:
"Reuters • 2h ago"

**Savings: 85%**

### 7. **Takeaway Efficiency**

❌ Long form (28 tokens):
"This development indicates that the market is moving towards increased consolidation in the technology sector, which could have significant implications for smaller companies."

✅ Punchy (8 tokens):
"M&A acceleration in tech sector consolidation."

**Savings: 71%**

---

## Briefing Length Strategy

### Ideal Token Distribution
| Component | Tokens | % of Total |
|---|---|---|
| System Prompt | 350 | 24% |
| Header/Metadata | 100 | 7% |
| 5-6 News Items | 850 | 59% |
| Footer/Navigation | 50 | 3% |
| **Total** | **1,350** | **100%** |

### Calculation Formula
```
Tokens = (Words × 1.3) + (Emojis × 0.5) + (Punctuation × 0.1)
```

---

## Item-Level Optimization

### Target Per Item
- **Headline**: 8-12 words (10-15 tokens)
- **Summary**: 40-60 words (50-80 tokens)
- **Takeaway**: 8-12 words (10-15 tokens)
- **Total per item**: 70-110 tokens

### Checklist
- [ ] No adjectives unless essential (great, amazing, significant = 3 tokens wasted)
- [ ] No repetition from headline to summary
- [ ] Numbers used as numerals (20 not "twenty")
- [ ] Dates abbreviated (June 20, 2024 → 6/20/24)
- [ ] All names shortened to essentials

---

## Category Selection Strategy

Choose **6 categories max** per briefing (7 if especially important day):

**High-token categories** to limit:
- Business (tends toward longer explanations)
- Global (often complex geopolitical context)

**Low-token categories** to maximize:
- Tech (can use more abbreviations)
- Science (structure lends itself to bullets)
- Breaking (inherently concise)

---

## Real-World Example

### Before Optimization
**Topic**: Tech M&A

```
🟢 TECH — Major Acquisition Reshapes AI Industry
Source: The Wall Street Journal
⏱️ 3 hours ago

In a significant development for the artificial intelligence sector, TechCorp announced today that it has acquired SmartAI Inc. for a valuation of five hundred million dollars. SmartAI has been developing cutting-edge language models and has gained recognition in the industry for its innovative approach to machine learning. According to the announcement, the acquisition will strengthen TechCorp's position in the rapidly growing AI market. Industry analysts believe this deal signals an important trend of consolidation in the sector.

→ This merger demonstrates the accelerating pace of AI market consolidation and could trigger similar transactions among other major players in the technology industry.
```

**Token count: 155 tokens**

### After Optimization
```
🟢 TECH — TechCorp Buys SmartAI for $500M
Source: WSJ
⏱️ 3h ago

TechCorp acquires SmartAI to strengthen AI capabilities. Deal marks major sector consolidation amid rapid market growth.

→ AI M&A acceleration signals investor confidence & industry reshaping.
```

**Token count: 38 tokens**
**Reduction: 75% fewer tokens, same information**

---

## Pro Tips

1. **Use emoji parsing** — Emojis compress information (🔴 = "Breaking") and are 0.5 tokens vs. 1+ for text

2. **Leverage formatting** — Bullets, bold, lists are more token-efficient than prose

3. **Link instead of explain** — Provide source links, let readers dig deeper if interested

4. **Batch similar items** — "3 tech M&A deals announced" instead of separate items (saves 40%)

5. **Template reuse** — Your format becomes muscle memory and compresses explanations naturally

6. **Remove articles** — "The company" → "Company" (saves 1 token per instance)

7. **Active voice only** — "Company launches X" (3 words) vs. "X was launched by the company" (6 words)

---

## Token Budget by Briefing Length

| Length | Items | Tokens/Item | Total Content | With System Prompt |
|---|---|---|---|---|
| Minimal | 3 | 60 | 180 | 530 |
| Concise | 5 | 80 | 400 | 750 |
| Standard | 6 | 90 | 540 | 890 |
| Comprehensive | 7 | 110 | 770 | 1,120 |
| Full | 8 | 120 | 960 | 1,310 |

**Recommendation**: Aim for "Standard" (6 items, ~890 tokens with system prompt) for best quality-to-token ratio.

---

## Monitoring Tools

To check token usage in Claude:
1. Copy your briefing text
2. Paste into token counter: https://token-counter.vercel.app/
3. Multiply words by 1.3 as estimate for Claude
4. Adjust summary lengths to hit target

---

## Advanced Optimization: JSON Format

For absolute token efficiency, use JSON:

```json
{
  "date": "6/20/24",
  "items": [
    {
      "cat": "TECH",
      "headline": "TechCorp buys SmartAI/$500M",
      "source": "WSJ",
      "time": "3h",
      "summary": "Major acquisition strengthens AI position; signals consolidation",
      "takeaway": "M&A accelerates in AI sector"
    }
  ]
}
```

**Savings**: ~35% fewer tokens than HTML/markdown. Use for API/automated briefings.
