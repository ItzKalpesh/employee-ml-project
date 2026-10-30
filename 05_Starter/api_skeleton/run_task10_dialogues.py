
import pandas as pd
import httpx

# Load the supplied Task 10 dialogue dataset.
df = pd.read_csv("../../data/chatbot_dialogues.csv")

results = []

for dialogue_id, group in df.groupby("dialogue_id", sort=False):

    session_id = f"task10-{dialogue_id}"

    role = str(group.iloc[0]["user_role"]).lower()
    employee_id = "EMP-0011" if role == "hr" else "EMP-0002"

    headers = {"X-Demo-User": employee_id}

    for _, row in group.iterrows():

        message = str(row["text"])
        expected = str(row["expected_intent"])

        try:
            response = httpx.post(
                "http://127.0.0.1:8001/v1/chat",
                headers=headers,
                json={
                    "message": message,
                    "session_id": session_id,
                },
                timeout=15,
            )

            response.raise_for_status()
            data = response.json()

            actual = data["intent"]
            reply = data["reply"]

            status = "PASS" if actual == expected else "FAIL"

        except Exception as exc:
            actual = "ERROR"
            reply = str(exc)
            status = "ERROR"

        results.append({
            "dialogue_id": dialogue_id,
            "turn": row["turn_no"],
            "message": message,
            "expected_intent": expected,
            "actual_intent": actual,
            "status": status,
            "reply": reply,
        })

        print(
            f"{dialogue_id} | Turn {row['turn_no']} | "
            f"{status} | Expected: {expected} | Actual: {actual}"
        )

# Save detailed results.
report = pd.DataFrame(results)

report.to_csv(
    "../../reports/task10_dialogue_test_results.csv",
    index=False,
)

# Print summary.
print("\n========== TASK 10 DIALOGUE SUMMARY ==========")

print(report["status"].value_counts().to_string())

total = len(report)
passed = (report["status"] == "PASS").sum()
failed = (report["status"] == "FAIL").sum()
errors = (report["status"] == "ERROR").sum()

print(f"\nTotal turns: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Errors: {errors}")

print(f"\nAccuracy: {(passed / total) * 100:.2f}%")

print(
    "\nDetailed results saved to "
    "reports/task10_dialogue_test_results.csv"
)

# Display failed turns separately.
failures = report[report["status"] != "PASS"]

if not failures.empty:
    print("\n========== FAILED TURNS ==========")
    print(
        failures[
            [
                "dialogue_id",
                "turn",
                "message",
                "expected_intent",
                "actual_intent",
            ]
        ].to_string(index=False)
    )
