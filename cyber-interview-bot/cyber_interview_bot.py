#!/usr/bin/env python3
"""
Interactive Cybersecurity Interview Coach (CLI)

Features:
- Ask mixed technical/scenario/behavioral questions
- Choose difficulty (Basic / Intermediate / Advanced)
- Evaluate answers with simple heuristics (keywords, STAR detection)
- Provide scores, strengths/weaknesses, actionable tips
- Adaptive flow (adjust difficulty based on performance)
- Explain concepts when requested
"""
import json
import os
import random
import re
import statistics
import datetime

ROOT = os.path.dirname(__file__)
QUESTIONS_PATH = os.path.join(ROOT, "questions.json")
SESSION_LOG = os.path.join(ROOT, "session_log.txt")


def load_questions(path=QUESTIONS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def choose_questions(questions, count=5, difficulty="Intermediate", mix=True):
    pool = [q for q in questions if q["difficulty"].lower() == difficulty.lower()]
    if not pool:
        # fallback to all
        pool = questions
    if mix:
        # ensure mix of categories if possible
        random.shuffle(pool)
    return pool[:count]


def get_multiline_input(prompt="Your answer (end with a single blank line):"):
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "":
            # blank line ends input
            break
        lines.append(line)
    return "\n".join(lines).strip()


def evaluate_answer(question, answer_text):
    """Return score (0-10), reasoning, strengths, weaknesses, tips"""
    if not answer_text:
        return 0, "No answer provided.", [], ["No response."], ["Try to answer the question; use STAR for behavioral answers or outline steps for technical ones."]

    qtype = question.get("type", "technical")
    keywords = question.get("keywords", [])
    explanation = question.get("explanation", "")
    score = 0
    strengths = []
    weaknesses = []
    tips = []
    reasoning_parts = []

    # Basic heuristics for technical questions: keyword coverage + explanation length
    if qtype == "technical":
        if keywords:
            matched = 0
            ans_lower = answer_text.lower()
            for kw in keywords:
                if kw.lower() in ans_lower:
                    matched += 1
            coverage = matched / len(keywords)
            score = round(coverage * 8)  # up to 8 from keywords
            reasoning_parts.append(f"Keyword coverage: {matched}/{len(keywords)}")
            if coverage > 0.7:
                strengths.append("Covered most key concepts")
            else:
                weaknesses.append("Missed some important concepts")
                tips.append("Make sure to mention the core terms and explain how they fit together. Consider a short definition followed by an example.")
        else:
            # fallback: length-based
            score = min(6, len(answer_text.split()) // 20)

        # length bonus: encourage concise but sufficiently detailed answers
        word_count = len(answer_text.split())
        if word_count > 120:
            score = min(10, score + 1)
            strengths.append("Provided detailed answer")
        elif word_count < 30:
            score = max(0, score - 1)
            weaknesses.append("Answer was short; expand with steps or examples")

        # final scaling to 0-10
        score = max(0, min(10, score))

        # add reasoning
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Evaluated technical response by heuristics."
        if explanation and score < 6:
            tips.append("Review the key concept: " + explanation)

    elif qtype == "behavioral":
        # detect STAR components: Situation, Task, Action, Result
        ans_lower = answer_text.lower()
        star_hits = 0
        for kw in ["situation", "task", "action", "result", "challenge", "led", "implemented", "outcome", "impact", "responsib"]:
            if kw in ans_lower:
                star_hits += 1
        # A simple scoring: presence of STAR-like structure and metrics
        score = min(10, star_hits * 2)
        if re.search(r"\b(\d+%|\d+\s+(days|weeks|months|years)|reduced|improved|decreased|increased)\b", ans_lower):
            score = min(10, score + 2)
            strengths.append("Included measurable results or metrics")
        if star_hits >= 3:
            strengths.append("Clear structure — covers multiple STAR elements")
        else:
            weaknesses.append("Missing parts of the STAR structure (Situation, Task, Action, Result)")
            tips.append("Use the STAR method: briefly state the Situation and Task, describe Actions you took, and end with the Result (preferably quantifiable).")
        reasoning = f"Detected STAR-like keywords: {star_hits}"
    else:
        # scenario-based: mix heuristics
        # use keywords if present, otherwise look for structured steps
        ans_lower = answer_text.lower()
        matched = 0
        for kw in keywords:
            if kw.lower() in ans_lower:
                matched += 1
        coverage = matched / len(keywords) if keywords else 0
        score = round(coverage * 7)
        if "step" in ans_lower or "first" in ans_lower or "then" in ans_lower:
            score += 2
            strengths.append("Provided a stepwise approach")
        if coverage < 0.5:
            weaknesses.append("Missed some technical or process-oriented items")
            tips.append("Outline a clear step-by-step plan and mention key controls or mitigations.")
        reasoning = f"Scenario heuristic: {matched}/{len(keywords) if keywords else 0} keywords matched"

    # final polish
    if score >= 8:
        strengths.append("Good answer — clear and thorough")
    elif score >= 5:
        strengths.append("Decent answer; with room to add more specifics or examples")

    brief_reason = f"Score: {score}/10. {reasoning}"
    return score, brief_reason, strengths, weaknesses, tips


def give_feedback(score, strengths, weaknesses, tips):
    print("\n--- Feedback ---")
    print(f"Score: {score}/10")
    if strengths:
        print("Strengths:")
        for s in strengths:
            print(f" - {s}")
    if weaknesses:
        print("Areas to improve:")
        for w in weaknesses:
            print(f" - {w}")
    if tips:
        print("Actionable tips:")
        for t in tips:
            print(f" - {t}")
    print("----------------\n")


def explain_concept(question):
    explanation = question.get("explanation", None)
    refs = question.get("references", [])
    if explanation:
        print("\n--- Explanation / Simplified ---")
        print(explanation)
    else:
        print("No detailed explanation available for this question.")
    if refs:
        print("References to look for (titles/topics):")
        for r in refs:
            print(f" - {r}")
    print("-------------------------------\n")


def log_session(entry):
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def interactive_session():
    questions = load_questions()
    print("Welcome to the Cybersecurity Interview Coach — CLI edition")
    print("You can type 'help' at any time for commands.")

    # preferences
    difficulty = "Intermediate"
    while True:
        d = input("Choose difficulty (Basic / Intermediate / Advanced) [Intermediate]: ").strip()
        if d == "":
            break
        if d.lower() in ("basic", "intermediate", "advanced"):
            difficulty = d.title()
            break
        print("Please enter Basic, Intermediate, or Advanced.")

    try:
        count = int(input("How many questions would you like? [5]: ") or 5)
    except ValueError:
        count = 5

    pool = choose_questions(questions, count=count, difficulty=difficulty)
    scores = []
    details = []

    for i, q in enumerate(pool, start=1):
        print(f"\nQuestion {i}/{len(pool)} — ({q.get('type','technical').title()}, {q.get('difficulty')})")
        print(q["question"])
        print("(Commands while answering: type 'explain' to see a simplified explanation after answering, 'skip' to skip, 'quit' to finish session.)")
        user_ans = get_multiline_input()

        if user_ans.strip().lower() == "quit":
            print("Ending session early.")
            break
        if user_ans.strip().lower() == "skip":
            print("Skipped.")
            scores.append(0)
            details.append((q, 0, "skipped"))
            continue

        score, reason, strengths, weaknesses, tips = evaluate_answer(q, user_ans)
        give_feedback(score, strengths, weaknesses, tips)
        scores.append(score)
        details.append((q, score, reason))

        # log
        ts = datetime.datetime.utcnow().isoformat()
        log_entry = f"{ts}\t{difficulty}\tQ:{q.get('id')}\tScore:{score}\tReason:{reason}"
        log_session(log_entry)

        # adaptive: adjust difficulty mid-session modestly
        avg = statistics.mean(scores) if scores else 0
        if avg >= 8 and difficulty != "Advanced":
            difficulty = "Advanced"
            print("Adaptive hint: raising difficulty to Advanced based on strong performance.")
        elif avg <= 3 and difficulty != "Basic":
            difficulty = "Basic"
            print("Adaptive hint: lowering difficulty to Basic to focus on fundamentals.")

        # prompt to explain if user wants
        while True:
            nxt = input("Type 'explain' for a concept explanation, 'continue' for next question, or 'quit' to finish: ").strip().lower()
            if nxt in ("continue", "c", ""):
                break
            if nxt == "explain":
                explain_concept(q)
            elif nxt == "quit":
                print("Ending session.")
                i = len(pool)  # will break outer
                break
            else:
                print("Unknown command. Use 'explain', 'continue', or 'quit'.")

    # session summary
    print("\n=== Session Summary ===")
    if scores:
        avg = round(statistics.mean(scores), 2)
        print(f"Average score: {avg}/10 over {len(scores)} answered questions")
        print("Question breakdown:")
        for q, s, reason in details:
            print(f" - Q{id(q)} | {q.get('type')} | {q.get('difficulty')} => {s}/10")
    else:
        print("No scored answers in this session.")

    print("Thanks for practicing — keep iterating on the tips and focus on measurable results and clear structure.")


if __name__ == '__main__':
    interactive_session()
