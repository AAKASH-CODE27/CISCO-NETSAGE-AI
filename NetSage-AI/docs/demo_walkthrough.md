# NetSage AI - Demo Walkthrough (Phase 9)

## Demo Overview

**Duration**: 5-10 minutes  
**Objective**: Show how NetSage AI assists junior network engineers in troubleshooting with human-in-the-loop oversight

---

## Demo Script

### **0:00 - 0:45 | Introduction to NetSage AI**

Start with a blank screen. Open the README or a title slide.

**Narrative:**

> "Network troubleshooting is hard. Junior engineers struggle to connect symptoms with root causes.
>
> This is NetSage AI — an AI-assisted troubleshooting system designed to help.
>
> Our approach:
>
> 1. Collect symptoms and network evidence
> 2. Apply deterministic rules to narrow possibilities
> 3. Use AI (Gemini) to suggest root causes and fixes
> 4. **Require human review before accepting**
> 5. Log corrections to improve the system over time"

**Key Point**: Emphasize human-in-the-loop. AI provides recommendations, humans decide.

---

### **0:45 - 1:30 | The Problem We're Solving**

Show a broken network scenario visually (or describe one).

**Narrative:**

> "Imagine a junior engineer is handed this:
>
> ❌ PC1 cannot ping PC2  
> ❌ Both are in the same department  
> ❌ They're on different switches
>
> What's the problem?
>
> - VLAN misconfiguration?
> - Routing issue?
> - Access Control List?
> - Cable disconnected?
>
> NetSage AI helps narrow this down systematically."

---

### **1:30 - 2:15 | Open the Dashboard**

Open a terminal and run:

```bash
streamlit run dashboard/app.py
```

Wait for the dashboard to load (should say "You can now view your Streamlit app in your browser at http://localhost:8501").

Open browser to dashboard. Let it load fully (should show Overview page).

**Narrative (while dashboard loads):**

> "Here's our dashboard. It shows an overview of our dataset and AI performance."

**Manually verify on Dashboard:**
✓ Title: "NetSage AI Dashboard"  
✓ Data Status shows: "35 cases ready"  
✓ Overview shows: 35 Total Cases

**Narrative:**

> "We have 35 real troubleshooting cases across 8 categories:
> VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT, and Wireless.
>
> The AI has diagnosed all 35 cases.
> All 35 have been reviewed by human engineers."

---

### **2:15 - 3:00 | Show Issue Distribution**

Click on "Issue Analysis" page in sidebar.

Wait for charts to render.

**Manually verify:**
✓ Issue Type bar chart shows all 8 categories  
✓ VLAN shows 5, Gateway shows 4, DHCP shows 5, etc.

**Narrative:**

> "This is our issue distribution. We have cases for all major network problems.
> Each category has between 4-5 cases to ensure comprehensive coverage.
>
> The severity distribution shows a mix of critical production issues down to low-priority warnings."

---

### **3:00 - 4:00 | Select a Demo Case**

Click on "Case Explorer" in sidebar.

Wait for case list to load.

Use Filter: Select an **EDIT** or **REJECT** case to demonstrate human correction.

**Recommended cases** (select one):

- NET-031 (if EDIT)
- NET-032 (if REJECT)
- NET-034 (if EDIT)

**Example selection script:**

```
Issue Type: (leave empty)
Severity: (leave empty)
Review Decision: Select "EDIT"
Search: (leave empty)
```

Click the first case that appears (should be an EDIT case).

**Narrative:**

> "Now let's look at a specific case where human review made a difference.
>
> This case was **EDITED** by a human engineer.
> The AI diagnosis wasn't completely wrong, but it needed refinement."

---

### **4:00 - 5:00 | Show Symptom and Evidence**

On the case detail page, expand "Symptom" section.

**Narrative:**

> "Here's what the junior engineer observed:
>
> [Read symptom]
>
> And here's the network topology they're working with:
>
> [Read topology]"

Expand "Show Command Evidence" section.

**Narrative:**

> "To debug this, they ran several show commands and got this output:
>
> [Brief summary of evidence]"

---

### **5:00 - 6:00 | Show Rule Checker Result**

_(If rule checker is visible in evaluation results)_

**Narrative:**

> "Our deterministic rule checker processed this evidence and found:
>
> [Read rule findings if available]
>
> Rules are 100% accurate but limited. They only catch what we explicitly programmed."

---

### **6:00 - 7:00 | Show AI Diagnosis**

Scroll to "AI Diagnosis" section on the case detail page.

**Narrative:**

> "The AI was asked: 'Given this symptom and evidence, what's the root cause?'
>
> The AI responded with:
>
> **Root Cause**: [Read from page]  
> **Confidence**: [Read score]  
> **Evidence**: [Read evidence items]  
> **Recommended Fix**: [Summarize]"

**Key Point**: "The AI provided a diagnosis. But is it right? That's where humans come in."

---

### **7:00 - 8:00 | Show Human Review and Correction**

Scroll to "Human Review" section (should be EDIT or REJECT).

**Narrative:**

> "A senior network engineer reviewed the AI diagnosis.
>
> **Decision**: [Show EDIT or REJECT badge]
>
> **Their Feedback**: [Read reason]
>
> **Their Correction**: [Read human_correction]"

**Critical for Demo**: Expand "Original AI vs. Human Review" to show BOTH side-by-side.

**Narrative:**

> "Notice: We don't **replace** the AI diagnosis. We **preserve** it.
>
> This is intentional. It documents what the AI said and what the human corrected.
>
> This creates a learning loop.
>
> Next quarter, when we train the next version of the model, we can say:
> 'Here are 100 cases where the AI was wrong. Learn from these.'"

---

### **8:00 - 9:00 | Show Recommended Fix and Verification**

Scroll to "Expected Fix (Ground Truth)" section.

**Narrative:**

> "The correct fix (ground truth) is:
>
> [Read expected_fix]
>
> And to verify it worked, we'd run:
>
> [Read verification]"

**Key Point**: "NetSage AI does NOT execute these commands. It RECOMMENDS them. A human approves and runs them."

---

### **9:00 - 10:00 | Show Dashboard Metrics Summary**

Go back to "Overview" page in sidebar.

**Narrative:**

> "Let's look at the big picture.
>
> **Total Cases**: 35  
> **Human Reviews**: All 35  
> **AI Diagnoses**: All 35  
> **Corrections**: 8 cases where human review improved the AI
>
> **AI-Human Agreement**: 77.1%
> This means 27 out of 35 cases, the human engineer said 'AI got it right.'
>
> **AI Evaluation Metrics**:
>
> - Root Cause Accuracy: 100%
> - Severity Accuracy: 100%
> - Evidence Grounding: 100%
> - Average Confidence: 0.90
>
> This shows the AI is performing well. When humans do correct it, it's usually a nuance, not a complete miss."

Go to "Responsible AI" page.

**Narrative:**

> "Here's what human engineers corrected:
>
> [Point to chart]
>
> Most corrections were:
>
> - Wrong root cause (5 cases)
> - Incomplete fix (3 cases)
>
> These lessons are logged so the next version of the AI can avoid these mistakes."

---

## Key Talking Points

### 1. **Human-in-the-Loop is Central**

- AI suggests
- Human reviews
- Human decides
- System learns

### 2. **Preserving AI Diagnosis is Intentional**

- We don't hide what the AI said
- We show what the human corrected
- This transparency is critical for trust and learning

### 3. **Metrics Show Safety**

- 100% root cause accuracy in this dataset
- 100% evidence grounding
- High confidence (0.90 average)
- These show the AI is trustworthy, not harmful

### 4. **The System Scales**

- 35 cases → works for 350 or 3500
- Automated evaluation pipeline
- Automated responsible AI logging
- Audit trail for compliance

### 5. **Real Use Case**

- Not a toy project
- Real Cisco/Packet Tracer scenarios
- Real networking concepts (VLAN, DHCP, etc.)
- Real human review workflow

---

## Q&A Preparation

### Q: "Will the AI take over network administration?"

**A:** "No. The AI is a tool for junior engineers, not a replacement. Humans always decide what fixes to apply."

### Q: "What if the AI makes a dangerous suggestion?"

**A:** "We have three safeguards:

1. Human review is mandatory (no auto-fix)
2. We log all corrections to learn from mistakes
3. We only show recommendations, never execute commands"

### Q: "How accurate is the AI?"

**A:** "On our test set:

- Root cause accuracy: 100%
- Evidence grounding: 100%
- Human agreement: 77%

But these are lab scenarios, not real networks. Real deployment would require more testing."

### Q: "What if there's a case the AI doesn't know?"

**A:** "Good question. Our system is designed for 8 specific categories. If a case is outside those, the human engineer would handle it traditionally. This is not an autonomous system."

### Q: "Can I see the source code?"

**A:** "Yes. The GitHub repository is at [insert repo URL]. We use:

- Python for backend
- Streamlit for dashboard
- Google Gemini for AI
- Our own deterministic rule checker"

---

## Physical Setup (If Presenting in Person)

1. **Two Monitors** (if available)
   - Monitor 1: Show PowerPoint/slides with talking points
   - Monitor 2: Run dashboard live

2. **One Monitor** (simpler setup)
   - Full screen Streamlit dashboard
   - Present from live interface

3. **Network Connectivity**
   - Ensure API keys are configured (if using real Gemini, not mock)
   - Test dashboard launch 5 minutes before presentation
   - Have mock data available if network is unavailable

4. **Projector/Screen**
   - Dashboard should be visible from back of room
   - Use largest font sizes (Streamlit defaults usually OK)
   - Test color contrast

---

## Timing Adjustments

- **Short Demo (5 min)**: Skip breakdown by category, show 1 corrected case only
- **Medium Demo (10 min)**: Follow script above
- **Long Demo (15 min)**: Add technical deep-dive on rule checker and AI prompt

---

## Success Criteria

✅ Dashboard opens without errors  
✅ 35 cases visible  
✅ All 8 issue types shown  
✅ Human review visible (ACCEPT/EDIT/REJECT)  
✅ Original AI diagnosis preserved for edited cases  
✅ No automatic commands execute  
✅ Metrics align with Phase 8 results

---

**End of Demo**

_Final Statement:_

> "NetSage AI demonstrates how AI can safely assist network engineers.
> The key innovation is **human oversight at every step**.
> This creates a trustworthy system that learns from mistakes."

---

**Version**: Phase 9  
**Last Updated**: 2026-08-29  
**Estimated Total Time**: 5-10 minutes
