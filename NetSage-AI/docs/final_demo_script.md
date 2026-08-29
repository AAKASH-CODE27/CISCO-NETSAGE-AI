# NetSage AI - Final Demonstration Script

## 5–10 Minute Presentation

---

## PRESENTATION OVERVIEW

**Objective**: Demonstrate a complete AI-assisted network troubleshooting workflow from problem to solution.

**Demo Case**: NET-031 (VLAN Misconfiguration)

**Duration**: 5–10 minutes

**Audience**: Technical reviewers, professors, project evaluators

---

## TIMING & SCRIPT

### 0:00–0:45 — **INTRODUCTION** (45 seconds)

**Presenter Says**:

"Hello, I'm [Name]. This is **NetSage AI**, an intelligent network troubleshooting system that combines rule-based evidence validation with Generative AI to diagnose network problems while maintaining human oversight.

The key principle: **AI recommends, humans decide.**

Today, I'll walk you through a real network problem—a host can't communicate with another VLAN—and show how NetSage AI helps diagnose and fix it.

Let's get started."

**Visuals**:

- Show title slide
- Display architecture diagram (data → rules → AI → human → decision)

---

### 0:45–1:30 — **THE PROBLEM** (45 seconds)

**Presenter Says**:

"Here's the scenario. We have a network with two VLANs:

- **VLAN 1**: Management (users and admin PCs)
- **VLAN 50**: Engineering (servers)

A host named 'Host_C' was just connected to switch port Fa0/5. The user reports: **'I can't reach the engineering servers.'**

Let me show you what we see when we run network diagnostics."

**Visuals**:

- Open Cisco Packet Tracer
- **Click and highlight**:
  - PC1 in VLAN 1 (working)
  - Host_C in VLAN 1 (broken, should be VLAN 50)
  - SRV1 in VLAN 50 (target server)
  - Topology showing SW1, SW2, CORE_R1

**Show Packet Tracer Broken State**:

```
Host_C> ping 192.168.50.10
Sending 5, 100-byte ICMP Echoes to 192.168.50.10, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)   ← FAILS
```

---

### 1:30–2:15 — **EVIDENCE COLLECTION** (45 seconds)

**Presenter Says**:

"Next, we collect evidence using standard Cisco show commands. This is critical—good diagnosis requires accurate evidence."

**In Packet Tracer**:

- Click on SW1, go to CLI
- Show these commands:

```
SW1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- ----------------------------------
1    Management                       active    Fa0/1, Fa0/5, ...
50   Engineering                      active    Fa0/10, ...

SW1# show interfaces FastEthernet0/5 switchport
Name: FastEthernet0/5
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 1
```

**Presenter Says**:

"See this? Port Fa0/5 is assigned to VLAN 1 (default management), not VLAN 50 where it should be. That's the problem—the host is in the wrong VLAN."

---

### 2:15–3:00 — **RULE CHECKER VALIDATION** (45 seconds)

**Presenter Says**:

"Before we involve AI, our system runs a deterministic rule checker. It validates the evidence automatically.

Rules like:

- 'Does this port match its expected VLAN?'
- 'Is the default gateway in the same subnet as the host IP?'
- 'Are all required VLANs configured?'

These rules are objective and verifiable—no AI hallucination here."

**Show/Open**:

- Terminal or Jupyter notebook
- Run: `python -m rule_checker` (or show output)

**Display**:

```
RULE CHECK RESULTS
──────────────────
✗ Port Fa0/5 VLAN Assignment: FAIL
  Expected: VLAN 50
  Actual: VLAN 1

✓ VLAN 50 Exists: PASS
✓ Routing Configured: PASS
✓ Switch Configuration: PASS

Evidence Extracted:
  - Port: Fa0/5
  - Current VLAN: 1
  - Host IP: 192.168.1.101
  - Target Server IP: 192.168.50.10
  - Root Cause Likelihood: Port Assignment
```

---

### 3:00–4:00 — **AI DIAGNOSIS** (60 seconds)

**Presenter Says**:

"Now the system sends this evidence to Google Gemini, an LLM, with a specific prompt.

The key here: **We don't let AI guess.** We feed it real evidence and ask it to reason step-by-step."

**Open the AI Diagnosis (can be in terminal, Jupyter, or saved output)**:

Display Gemini Response:

```
ROOT CAUSE ANALYSIS
───────────────────

Root Cause: Port Fa0/5 is unassigned and defaulting to VLAN 1.

Confidence: 0.89 (89%)

Reasoning:
1. Host_C is on port Fa0/5 which is in VLAN 1
2. Server is in VLAN 50
3. Host IP 192.168.1.101 is in VLAN 1 subnet
4. Cross-VLAN routing is configured on the router
5. But Host_C can't reach VLAN 50 because it's not a member of VLAN 50

Evidence Trail:
  - show vlan brief: Fa0/5 listed under VLAN 1
  - show interfaces Fa0/5 switchport: Access Mode VLAN = 1
  - ping test: Timeout (same VLAN PC1 reachable, but VLAN 50 servers unreachable)

Next Command to Run:
  show interfaces Fa0/5 switchport

Recommended Fix:
  Configure: switchport access vlan 50

Why This Works:
  Once Fa0/5 is assigned to VLAN 50, Host_C will be in the same VLAN as servers,
  and inter-VLAN routing will allow communication through CORE_R1.

Severity: Medium (affects specific host, not entire VLAN)
```

**Presenter Says**:

"The AI gives us a diagnosis with 89% confidence. It explains the reasoning, cites the evidence, and suggests the fix. But here's the critical part—it's **not autonomous**. We don't execute anything automatically. We hand it to a human."

---

### 4:00–5:00 — **HUMAN REVIEW** (60 seconds)

**Presenter Says**:

"A network engineer reviews the AI diagnosis and makes one of three decisions:

1. **ACCEPT**: The diagnosis is correct. Apply the fix.
2. **EDIT**: The diagnosis is mostly right but needs clarification.
3. **REJECT**: The diagnosis is wrong. Provide correct answer.

In this case, the engineer says: **EDIT**"

**Show Human Review Record** (from CSV or dashboard):

```
Case ID:              NET-031
AI Root Cause:        Port Fa0/5 defaulting to VLAN 1
AI Confidence:        0.89
Human Decision:       EDIT
Human Correction:     Port Fa0/5 is assigned to VLAN 1 (default) instead of VLAN 50 (Engineering)
Reason:               AI correctly identified the issue but human clarified the exact target VLAN (50)
Reviewer:             Lead Network Architect
Timestamp:            2026-08-28T10:20:00Z
```

**Presenter Says**:

"Why EDIT? The AI was right—VLAN 1 is wrong. But the human reviewer clarified: **VLAN 50 is specifically for Engineering.** This context matters. The original AI output is preserved here—you can see both the AI's reasoning and the human's feedback side-by-side. That's transparency."

---

### 5:00–6:00 — **MANUAL FIX APPLICATION** (60 seconds)

**Presenter Says**:

"Now, the engineer manually applies the fix in the network. No automation here—every change is deliberate and traceable."

**In Cisco Packet Tracer**:

- Click on SW1 CLI
- Type configuration:

```
SW1> enable
SW1# conf t
SW1(config)# interface FastEthernet0/5
SW1(config-if)# switchport access vlan 50
SW1(config-if)# exit
SW1(config)# exit
SW1#
```

**Presenter Says**:

"One command: `switchport access vlan 50`. That's it. We've moved the port from VLAN 1 to VLAN 50."

---

### 6:00–7:00 — **VERIFICATION** (60 seconds)

**Presenter Says**:

"Let's verify the fix works. Same commands as before, but now we expect different results."

**In Cisco Packet Tracer**:

- Check VLAN assignment:

```
SW1# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- ----------------------------------
1    Management                       active    Fa0/1, ...
50   Engineering                      active    Fa0/5, Fa0/10, ...  ← NOW HERE

SW1# show interfaces FastEthernet0/5 switchport
Name: FastEthernet0/5
Switchport: Enabled
Access Mode VLAN: 50    ← FIXED
```

- Test connectivity:

```
Host_C> ping 192.168.50.10
Sending 5, 100-byte ICMP Echoes to 192.168.50.10, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5)   ← SUCCESS!
```

**Presenter Says**:

"And it works. Host_C can now reach the engineering servers. Problem solved."

---

### 7:00–8:00 — **DASHBOARD OVERVIEW** (60 seconds)

**Presenter Says**:

"All of this is tracked and visualized in our interactive dashboard. Let me show you what we learn from analyzing many cases."

**Start Dashboard**:

```bash
streamlit run dashboard/app.py
```

**Navigate to Pages**:

1. **Overview Page** (15 seconds):
   - Show: "35 total cases"
   - Show: "27 ACCEPT, 5 EDIT, 3 REJECT"
   - Show: "77.1% AI-human agreement"
   - Say: "Most AI diagnoses are accepted by humans, but 23% need correction. That's expected—it means we're catching and fixing AI errors."

2. **Issue Analysis Page** (20 seconds):
   - Show: Distribution of issue types (VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT, Wireless)
   - Say: "We've tested the system across 8 different networking domains. VLAN issues are common, so we see 5 cases here."

3. **Case Explorer Page** (15 seconds):
   - Search for: "NET-031"
   - Show: Full case details
   - Point to: "Original AI diagnosis" and "Human correction" (side-by-side)
   - Say: "This is critical for learning. We never hide the AI's original reasoning. Both the AI and human inputs are visible. This creates an audit trail."

4. **Responsible AI Page** (10 seconds):
   - Show: "8 corrections out of 35 cases"
   - Show: Correction categories (WRONG_ROOT_CAUSE, INCOMPLETE_FIX)
   - Say: "When we make corrections, we categorize them. This helps us understand where AI fails and improve over time."

---

### 8:00–9:00 — **RESPONSIBLE AI & SAFETY** (60 seconds)

**Presenter Says**:

"Before I close, I want to highlight something important: **Safety and Responsible AI.**

This system is designed with three principles:

1. **No Autonomous Execution**: AI recommends. A human reads it. The human applies changes manually. No network commands run automatically from the AI.

2. **Transparency**: Original AI reasoning is never hidden, even when it's wrong. You can see both the AI's diagnosis and the human's correction. This is how we learn.

3. **Auditability**: Every case, every review, every correction is logged. We can trace why a decision was made, who made it, and when. If something goes wrong, we have a complete record."

**Show**:

- Open `results/responsible_ai_log.csv`
- Point to columns: Case ID, AI Confidence, Human Decision, Correction Category, Timestamp

**Presenter Says**:

"Here's the audit trail. 8 corrections across 35 cases. 5 cases where AI got the root cause wrong. 3 cases where AI's fix was incomplete. This data helps us improve the system."

---

### 9:00–9:30 — **KEY TAKEAWAYS** (30 seconds)

**Presenter Says**:

"NetSage AI shows that:

1. **Rule-Based + AI is Better Than Either Alone**
   - Rules provide evidence grounding (no hallucinations)
   - AI provides reasoning (no brute-force rule lists)
   - Together: robust, explainable, verifiable

2. **Human Oversight is Essential**
   - 23% of diagnoses need human correction—that's expected
   - AI confidence doesn't guarantee accuracy
   - Humans catch what algorithms miss

3. **Transparency Enables Learning**
   - Original AI preserved alongside corrections
   - Audit trail allows continuous improvement
   - Trust is built on visibility, not opacity"

---

### 9:30–10:00 — **CLOSING & QUESTIONS** (30 seconds)

**Presenter Says**:

"In summary: NetSage AI demonstrates how to responsibly integrate AI into critical network operations. It's not replacing network engineers—it's making them faster, more consistent, and more confident.

The system is ready to demonstrate, and all code is tested and documented.

Thank you. I'm happy to take any questions about the architecture, the dataset, the AI integration, or anything else."

---

## DEMO LOGISTICS

### Prerequisites

- Cisco Packet Tracer installed and NET-031 topology created
- Python environment set up (see requirements.txt)
- Google Gemini API key configured (or mock mode available)
- Streamlit installed

### Backup Plans

- **If Packet Tracer network fails**: Use screenshots of broken/fixed states
- **If AI API fails**: Show pre-recorded JSON responses
- **If dashboard won't start**: Show screenshots of dashboard pages
- **If time runs short**: Skip Packet Tracer details and jump to dashboard (6-minute version possible)

### Technical Setup (Before Demo)

```bash
# 1. Ensure Packet Tracer topology is created and saved
# Location: <NAME>-<COLLEGE NAME>-NetSageAI.pkt

# 2. Ensure Python environment is active
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows

# 3. Test dashboard startup
streamlit run dashboard/app.py
# Verify it opens at http://localhost:8501

# 4. Verify case data loads
python -m scripts.validate_cases
# Expected output: PASS

# 5. Have screenshots ready as backup
```

### Display Setup

- **Primary Monitor**: Cisco Packet Tracer + Terminals
- **Secondary Monitor** (if available): Dashboard preview
- **Projector/Presentation**: Full-screen toggle with Alt+Tab

### Timing Checkpoints

- 2:00 — Problem description + Packet Tracer should show broken ping
- 4:00 — AI diagnosis should be visible on screen
- 6:00 — Fix command applied, show vlan brief should show VLAN 50
- 7:00 — Ping should succeed, verify with 100% success
- 8:30 — Dashboard should be fully loaded with all pages responsive

---

## QUESTIONS LIKELY TO COME UP

**Q: "Why not just let the AI fix the network automatically?"**
A: "Because network changes can have unintended consequences. A human must review and manually apply fixes to ensure safety. This is the entire principle of the system—AI recommends, human decides."

**Q: "How accurate is the AI?"**
A: "On our test dataset of 35 cases, there was 77.1% agreement between AI diagnosis and human review. The mock evaluation shows 100% accuracy, but that's validating our infrastructure, not production AI performance. Real Gemini accuracy would need to be measured separately."

**Q: "What happens with multiple simultaneous network problems?"**
A: "The current system is designed for single-fault diagnosis. Multiple simultaneous faults would require either multiple rule iterations or enhancements to the system design. That's future work."

**Q: "Can this integrate with our existing NOC tools?"**
A: "The current system is standalone, but the architecture supports API creation. Future work could add REST endpoints for integration with ITSM tools, ticketing systems, etc."

**Q: "What if the AI hallucinates—makes up false evidence?"**
A: "We mitigate this through evidence grounding. The AI must cite specific evidence from the show-command outputs. Hallucinations would be caught in the human review step. Also, the rule checker pre-processes evidence to extract facts deterministically, so the AI starts with validated inputs, not raw text."

---

## DEMO SCRIPT VARIANTS

### **6-Minute Quick Version** (If time is short)

Skip Packet Tracer details. Start at 3:00 min mark (AI Diagnosis).

### **15-Minute Extended Version** (If time allows)

Add: Code walkthrough (show rule_checker.py, diagnosis.py, dashboard/app.py snippets)

### **Hands-On Variant** (If interactive Q&A preferred)

Pause at 5:00 min: "What should we change?" → Let audience suggest the fix

---

## CLOSING NOTE

This demo script is designed to be flexible. Adjust timing, skip sections, or go deeper based on audience interest. The goal is to demonstrate:

1. **Real Problem** (Packet Tracer network broken)
2. **Evidence-Based Approach** (show commands, rule checker)
3. **AI Integration** (Gemini diagnosis with reasoning)
4. **Human Oversight** (review decision, manual fix)
5. **Responsible AI** (audit trail, transparency, safety)

Good luck with your presentation!
