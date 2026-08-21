# utils/rag_metrics.py

import re
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import CrossEncoder
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
# ============================================================
# موديل الـSemantic Similarity (STS) - مختلف عن الـReranker
# الـReranker بيقيس "relevance" (هل الـchunk يجاوب السؤال)
# ده بيقيس "entailment/similarity" (هل الجملة فعلاً معناها موجود في الـevidence)
# ============================================================
semantic_scorer = CrossEncoder("cross-encoder/stsb-roberta-base")


def split_into_claims(answer: str) -> List[str]:
    """تقسيم الإجابة لجمل/claims منفصلة - بدون فصل الـ[Page X] عن جملتها"""
    sentences = re.split(r'(?<=[.!?])\s+(?!\[Page)', answer.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def extract_citation(claim: str) -> Tuple[str, str]:
    """
    يفصل رقم الصفحة المذكورة عن نص الـclaim.
    الفورمات المتوقع: "... [Page 45]."
    """
    match = re.search(r'\[Page\s*(\d+)\]', claim)
    page = match.group(1) if match else None
    clean_claim = re.sub(r'\[Page\s*\d+\]', '', claim).strip()
    return clean_claim, page


def calculate_faithfulness_hybrid(
    answer: str,
    evidence_chunks: List[Dict],  # كل dict فيه {"text":..., "page":...}
    lexical_weight: float = 0.4,
    semantic_weight: float = 0.6,
    threshold: float = 0.55
) -> Dict:
    """
    Hybrid Faithfulness: lexical overlap + semantic (STS) similarity.
    بيرجع النتيجة الكلية + تفصيل كل claim لوحده (للـtransparency في التقرير).
    """
    claims_raw = split_into_claims(answer)
    if not claims_raw:
        return {"faithfulness_score": 0.0, "details": []}

    evidence_texts = [c["text"] for c in evidence_chunks]
    full_evidence_tokens = set(" ".join(evidence_texts).lower().split())

    details = []
    supported_count = 0

    for raw_claim in claims_raw:
        clean_claim, cited_page = extract_citation(raw_claim)
        claim_tokens = set(clean_claim.lower().split())

        # --- Lexical score ---
        if claim_tokens:
            lexical_score = len(claim_tokens & full_evidence_tokens) / len(claim_tokens)
        else:
            lexical_score = 0.0

        # --- Semantic score (أعلى تشابه مع أي chunk) ---
        pairs = [(clean_claim, ev) for ev in evidence_texts]
        semantic_scores = semantic_scorer.predict(pairs) if pairs else [0.0]
        best_idx = int(np.argmax(semantic_scores))
        semantic_score = float(semantic_scores[best_idx])
        best_matching_page = evidence_chunks[best_idx]["page"] if evidence_chunks else None

        hybrid_score = (lexical_weight * lexical_score) + (semantic_weight * semantic_score)
        is_supported = hybrid_score >= threshold

        if is_supported:
            supported_count += 1

        details.append({
            "claim": clean_claim,
            "cited_page": cited_page,
            "best_evidence_page": best_matching_page,
            "lexical_score": round(lexical_score, 3),
            "semantic_score": round(semantic_score, 3),
            "hybrid_score": round(hybrid_score, 3),
            "supported": is_supported
        })

    faithfulness_score = supported_count / len(claims_raw)
    return {"faithfulness_score": round(faithfulness_score, 3), "details": details}


def calculate_citation_accuracy(faithfulness_details: List[Dict]) -> float:
    """
    بتاخد الـdetails الناتجة من calculate_faithfulness_hybrid وتحسب:
    من ضمن الـclaims اللي فيها citation، كام واحد فعلاً الصفحة المذكورة
    بتطابق (أو قريبة من) صفحة أقوى evidence.
    """
    cited_claims = [d for d in faithfulness_details if d["cited_page"] is not None]
    if not cited_claims:
        return 0.0

    correct = sum(
        1 for d in cited_claims
        if d["cited_page"] == str(d["best_evidence_page"])
    )
    return round(correct / len(cited_claims), 3)


def create_rag_safety_prompt(system_guidelines: str = "") -> str:
    """System prompt يفرض الالتزام بالـcontext + فورمات الـcitation + تحذير طبي"""
    base_prompt = (
        "### SYSTEM SAFETY & CONSTRAINT GUIDELINES ###\n"
        "1. You are a clinical RAG assistant. Answer STRICTLY and ONLY using the provided evidence text.\n"
        "2. Do NOT use external/general medical knowledge outside the retrieved context.\n"
        "3. After EVERY sentence containing a factual claim, add the exact page number in this format: [Page X].\n"
        "4. If the answer is not fully covered by the provided evidence, respond ONLY with: "
        "'I am sorry, but I can only answer questions based on the provided documents.'\n"
        "5. This is medical reference information, NOT a substitute for professional medical judgment. "
        "Never suggest a specific dosage or treatment decision for an individual patient.\n"
    )
    if system_guidelines:
        base_prompt += f"\nAdditional Constraints:\n{system_guidelines}"
    return base_prompt

REFUSAL_MESSAGE = "I am sorry, but I can only answer questions based on the provided documents."
# 1. إضافة دالة حساب الـ Faithfulness
def calculate_faithfulness(generated_answer, retrieved_context):
    if not retrieved_context or not generated_answer:
        return 0.0
    
    answer_words = set(generated_answer.lower().split())
    context_words = set(retrieved_context.lower().split())
    
    overlap = answer_words.intersection(context_words)
    score = len(overlap) / len(answer_words) if answer_words else 0.0
    return round(score, 2)


# 2. Guardrail يدمج الـ Faithfulness والـ Refusal
# 2. Guardrail يدمج الـ Faithfulness والـ Refusal
# 2. Guardrail يدمج الـ Faithfulness والـ Refusal
def enforce_safety_guardrail(generated_answer: str, retrieved_context: str, threshold: float = 0.4) -> dict:
    # حماية ضد إن الـ context يكون None أو مش نص
    if not retrieved_context or not isinstance(retrieved_context, str) or not retrieved_context.strip():
        return {
            "final_answer": REFUSAL_MESSAGE,
            "was_blocked": True,
            "original_answer": generated_answer if generated_answer else "",
            "faithfulness_score": 0.0,
            "reason": "No retrieved context provided - failing safe"
        }
    
    # ... باقي كود الدالة زي ما هو

    evidence_chunks = [{"text": retrieved_context, "page": 1}]
    hybrid_res = calculate_faithfulness_hybrid(generated_answer, evidence_chunks, threshold=threshold)
    faith_score = hybrid_res["faithfulness_score"]

    is_refusal = REFUSAL_MESSAGE.lower() in generated_answer.lower()

    if faith_score < threshold or is_refusal:
        return {
            "final_answer": REFUSAL_MESSAGE,
            "was_blocked": True,
            "original_answer": generated_answer,
            "faithfulness_score": faith_score,
            "reason": f"faithfulness_score ({faith_score}) below threshold ({threshold})" if not is_refusal else "Model self-refused"
        }

    return {
        "final_answer": generated_answer,
        "was_blocked": False,
        "original_answer": generated_answer,
        "faithfulness_score": faith_score,
        "reason": None
    }
import json
from sklearn.metrics import classification_report, accuracy_score

# 1. استدعاء الدالة الخاصة بنظام الـ RAG بتاعك
# استبدل الدالة دي بالدالة الفعلية اللي بتستقبل السؤال وترجع الإجابة أو الفلترة
def predict_relevance(question):
    # فحص بسيط مؤقت لتجربة التقييم
    keywords = ["malaria", "plasmodium", "artesunate", "quinine"]
    return any(kw in question.lower() for kw in keywords)  # ترجع True لو متعلق بالملاريا، و False لو غير متعلق

def predict_safety(question: str) -> bool:
    unsafe_keywords = [
        "home remedy", "self-medicate", "doubling the dose",
        "overdose", "without consulting", "ignore doctor",
        "stop taking", "expired", "breastfeeding without",
        "without prescription", "without a prescription", "contraindicated",
        "buy antibiotics", "over the counter antibiotic", "without seeing a doctor"
    ]
    
    # 1. فحص الكلمات غير الآمنة
    question_lower = question.lower()
    for kw in unsafe_keywords:
        if kw in question_lower:
            return False
            
    return True  # لو مفيش كلمات غير آمنة، نعتبر السؤال آمن