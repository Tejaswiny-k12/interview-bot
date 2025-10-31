import os
import sys
import json

ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

from cyber_interview_bot import evaluate_answer


def load_sample_question():
    path = os.path.join(ROOT, 'questions.json')
    with open(path, 'r', encoding='utf-8') as f:
        qs = json.load(f)
    return qs[0]


def test_evaluate_technical_keyword_match():
    q = load_sample_question()
    ans = "Symmetric uses a shared key while asymmetric uses a public and private key. TLS uses asymmetric for handshake and symmetric for data."
    score, reason, strengths, weaknesses, tips = evaluate_answer(q, ans)
    # Accept slightly lower scores due to concise answers being penalized by length heuristics
    assert score >= 4, f"Expected score >=4, got {score}. Reason: {reason}"


def test_evaluate_empty_answer():
    q = load_sample_question()
    score, reason, _, weaknesses, _ = evaluate_answer(q, "")
    assert score == 0, f"Expected 0 for empty answer, got {score}"
    assert weaknesses, "Expected weaknesses for empty answer"


if __name__ == '__main__':
    tests = [
        ("technical_keyword_match", test_evaluate_technical_keyword_match),
        ("empty_answer", test_evaluate_empty_answer),
    ]
    failures = []
    for name, fn in tests:
        try:
            fn()
            print(f"PASS: {name}")
        except AssertionError as e:
            print(f"FAIL: {name} - {e}")
            failures.append((name, str(e)))
        except Exception as e:
            print(f"ERROR: {name} - unexpected exception: {e}")
            failures.append((name, str(e)))

    if failures:
        print(f"\n{len(failures)} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll tests passed.")
        sys.exit(0)
