import os
import sys

# Offline Mode
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from rag_metrics import (
    calculate_faithfulness_hybrid,
    calculate_citation_accuracy,
    enforce_safety_guardrail,
    predict_safety
)

print("\n--- STARTING SYSTEM SANITY & UNIT TESTS ---\n")

# --- Test Case 1 ---
ans_1 = "Malaria is transmitted by female Anopheles mosquitoes. [Page 1]"
ctx_1 = [{"text": "Malaria is transmitted by female Anopheles mosquitoes. Details are documented here [Page 1].", "page": "1"}]

res_1 = calculate_faithfulness_hybrid(ans_1, ctx_1)
faith_1 = res_1.get("faithfulness_score", 0.0)
cite_1 = calculate_citation_accuracy(res_1.get("details", []))

print(f"Test 1 - High Faithfulness & Correct Citation:")
print(f"  -> Faithfulness: {faith_1:.2f} | Citation Accuracy: {cite_1:.2f}")

assert faith_1 >= 0.4, "❌ Failure in Test 1: Grounded answer scored low!"
assert cite_1 == 1.0, "❌ Failure in Test 1: Valid citation was rejected!"
print("  ✅ PASS: Test 1 Passed Successfully.\n")

# --- Test Case 2 ---
ans_2 = "The capital of France is Paris."
ctx_2 = [{"text": "Malaria is caused by Plasmodium parasites transmitted by mosquitoes.", "page": "1"}]

res_2 = calculate_faithfulness_hybrid(ans_2, ctx_2)
faith_2 = res_2.get("faithfulness_score", 0.0)

print(f"Test 2 - Hallucination Check:")
print(f"  -> Faithfulness: {faith_2:.2f}")

assert faith_2 < 0.3, "❌ Failure in Test 2: Hallucination was not caught!"
print("  ✅ PASS: Test 2 Passed Successfully.\n")

# --- Test Case 3 ---
ans_3 = "Malaria is transmitted by mosquitoes. [Page 99]"
ctx_3 = [{"text": "Malaria is transmitted by female Anopheles mosquitoes. [Page 1]", "page": "1"}]

res_3 = calculate_faithfulness_hybrid(ans_3, ctx_3)
cite_3 = calculate_citation_accuracy(res_3.get("details", []))

print(f"Test 3 - Invalid Citation Page Check:")
print(f"  -> Citation Accuracy: {cite_3:.2f}")

assert cite_3 == 0.0, "❌ Failure in Test 3: Wrong citation page passed!"
print("  ✅ PASS: Test 3 Passed Successfully.\n")

# --- Test Case 4 ---
unsafe_q = "Is it safe to buy antibiotics without a prescription for severe fever?"
safe_q = "What are the primary symptoms of falciparum malaria?"

assert predict_safety(unsafe_q) == False, "❌ Failure in Test 4: Unsafe question bypassed Layer 1!"
assert predict_safety(safe_q) == True, "❌ Failure in Test 4: Safe question blocked incorrectly!"
print("  ✅ PASS: Test 4 Safety Filters Passed Successfully.\n")

print("==================================================")
print("🎉 ALL SANITY TESTS PASSED 100%! SYSTEM LOGIC IS VALIDATED.")
print("==================================================")