"""
ingest.py
---------
End-to-end ingestion pipeline:
  1. parse raw files in assets/documents
  2. split them into chunks
  3. embed the chunks
  4. store them in ChromaDB

Run directly with:  python -m src.ingestion.ingest
"""

from src.ingestion.parser import load_documents
from src.ingestion.chunker import chunk_documents
from src.embedder import embedder
from src.vectorstore.vector_store import vector_store


def run_ingestion(is_markdown: bool = True, model_name: str = "text-embedding-3-small") -> None:
    print("Loading documents...")
    documents = load_documents()
    print(f"  found {len(documents)} document(s)")

    if not documents:
        print("No documents found in src/assets/documents. Add some .txt/.md/.pdf files and re-run.")
        return

    print("Chunking documents...")
    chunks = chunk_documents(documents, is_markdown=is_markdown)
    print(f"  created {len(chunks)} chunk(s)")

    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed_documents(texts)

    print("Storing in ChromaDB...")
    vector_store.add_chunks(chunks, embeddings)

    print(f"Done. Vector store now has {vector_store.count()} chunk(s).")


if __name__ == "__main__":
    run_ingestion(is_markdown=True)

    

    #query = "What is the main topic of the documents?"

    #print(f"Querying vector store for: '{query}'")

    #query_embedding = embedder.embed_query(query)

    #results = vector_store.query(query_embedding, top_k=3)
    #print(f"Found {len(results)} result(s):")
    

    from src.retrieval.evaluator import evaluate_with_ranx

    from src.retrieval.retriever import retrieve

    test_cases = [
    {
        "question": "What causes malaria and how is it transmitted?",
        "answer": "Malaria is a potentially life-threatening infectious disease caused by Plasmodium parasites. It is most commonly transmitted through the bite of an infected female Anopheles mosquito.",
        "page": 1,
        "section": "1. Overview"
    },
    {
        "question": "Which Plasmodium species are recognized as important causes of human malaria?",
        "answer": "Five Plasmodium species are recognized as important causes of human malaria: P. falciparum, P. vivax, P. ovale, P. malariae, and P. knowlesi.",
        "page": 1,
        "section": "1. Overview"
    },
    {
        "question": "Which Plasmodium species is associated with the greatest risk of severe malaria and death?",
        "answer": "P. falciparum is associated with the greatest risk of severe malaria and death.",
        "page": 1,
        "section": "1. Overview"
    },
    {
        "question": "What happens during the malaria parasite life cycle after an infected mosquito bites a person?",
        "answer": "The mosquito injects sporozoites into the bloodstream. The sporozoites travel to the liver, invade hepatocytes, and multiply. Merozoites are then released into the blood and invade red blood cells, where repeated erythrocytic cycles produce the clinical manifestations of malaria.",
        "page": 1,
        "section": "2. Transmission and Life Cycle"
    },
    {
        "question": "What are hypnozoites and which malaria species can form them?",
        "answer": "Hypnozoites are dormant liver stages of the malaria parasite that can reactivate later and cause relapses. P. vivax and P. ovale can form hypnozoites.",
        "page": 1,
        "section": "2. Transmission and Life Cycle"
    },
    {
        "question": "Does P. falciparum form hypnozoites?",
        "answer": "No. P. falciparum does not form hypnozoites. Hypnozoites are associated with P. vivax and P. ovale.",
        "page": 1,
        "section": "2. Transmission and Life Cycle"
    },
    {
        "question": "What are the common clinical symptoms of malaria?",
        "answer": "Common symptoms include fever, chills, sweats, headache, malaise, myalgia, nausea, vomiting, and weakness.",
        "page": 1,
        "section": "3. Clinical Presentation"
    },
    {
        "question": "What physical findings may occur in patients with malaria?",
        "answer": "Physical findings may include pallor, jaundice, splenomegaly, hepatomegaly, and altered mental status.",
        "page": 1,
        "section": "3. Clinical Presentation"
    },
    {
        "question": "What laboratory abnormalities can occur in malaria?",
        "answer": "Laboratory abnormalities can include anemia, thrombocytopenia, elevated bilirubin, and other findings related to hemolysis or organ dysfunction.",
        "page": 1,
        "section": "3. Clinical Presentation"
    },
    {
        "question": "What are the important manifestations of severe malaria?",
        "answer": "Important manifestations include impaired consciousness or coma, repeated seizures, severe anemia, acute kidney injury, respiratory distress or pulmonary edema, shock, acidosis, hypoglycemia, significant bleeding, jaundice with other severe features, and high parasite density.",
        "page": 2,
        "section": "4. Severe Malaria"
    },
    {
        "question": "Why is severe malaria considered a medical emergency?",
        "answer": "Severe malaria is a medical emergency because it can rapidly cause life-threatening complications such as impaired consciousness, seizures, severe anemia, acute kidney injury, respiratory distress, shock, acidosis, hypoglycemia, and organ dysfunction.",
        "page": 2,
        "section": "4. Severe Malaria"
    },
    {
        "question": "Which Plasmodium species is most strongly associated with severe malaria?",
        "answer": "Severe malaria is most strongly associated with P. falciparum, although severe disease can occur with other Plasmodium species.",
        "page": 2,
        "section": "4. Severe Malaria"
    },
    {
        "question": "What are the main laboratory methods used to diagnose malaria?",
        "answer": "The main diagnostic methods include microscopy of thick and thin blood smears and rapid diagnostic tests (RDTs). Molecular tests such as PCR can also provide sensitive species identification when available.",
        "page": 2,
        "section": "5. Diagnosis"
    },
    {
        "question": "What is the difference between thick and thin blood smears in malaria diagnosis?",
        "answer": "Thick blood smears are useful for detecting parasites because they concentrate blood, while thin blood smears help identify parasite morphology and estimate parasitemia.",
        "page": 2,
        "section": "5. Diagnosis"
    },
    {
        "question": "What is the role of rapid diagnostic tests in malaria diagnosis?",
        "answer": "Rapid diagnostic tests detect malaria parasite antigens and can be particularly useful when microscopy is not immediately available.",
        "page": 2,
        "section": "5. Diagnosis"
    },
    {
        "question": "Can a single negative malaria test always exclude malaria?",
        "answer": "No. A negative initial test does not always exclude malaria when clinical suspicion remains high. Repeat testing may be required depending on the clinical situation and local diagnostic guidance.",
        "page": 2,
        "section": "5. Diagnosis"
    },
    {
        "question": "What factors determine the treatment selected for malaria?",
        "answer": "Treatment depends on the infecting species, disease severity, geographic location where infection was acquired, local drug resistance, patient factors, and whether the infection is uncomplicated or severe.",
        "page": 2,
        "section": "6. Treatment Principles"
    },
    {
        "question": "What treatment approach is commonly used for uncomplicated malaria?",
        "answer": "Treatment depends on the infecting species, geographic location, drug resistance, and patient factors. Artemisinin-based combination therapies are commonly used for uncomplicated malaria when appropriate according to current treatment guidelines.",
        "page": 2,
        "section": "6. Treatment Principles"
    },
    {
        "question": "What is an important treatment principle for severe malaria?",
        "answer": "Severe malaria requires urgent parenteral antimalarial therapy. Intravenous artesunate is a key treatment in modern malaria treatment guidelines.",
        "page": 2,
        "section": "6. Treatment Principles"
    },
    {
        "question": "Why does P. vivax malaria require treatment beyond the blood stage?",
        "answer": "P. vivax can form dormant hypnozoites in the liver. These hypnozoites can reactivate and cause relapses, so treatment may need to include therapy directed against the liver stage.",
        "page": 2,
        "section": "6. Treatment Principles"
    },
    {
        "question": "Why should G6PD status be considered before using primaquine or tafenoquine?",
        "answer": "Primaquine and tafenoquine can cause hemolysis in patients with G6PD deficiency, so G6PD status should be considered before these drugs are used for radical cure.",
        "page": 2,
        "section": "6. Treatment Principles"
    },
    {
        "question": "What is radical cure in P. vivax and P. ovale malaria?",
        "answer": "Radical cure refers to treatment that targets both the blood-stage infection and the dormant liver hypnozoites in P. vivax or P. ovale, helping prevent future relapses.",
        "page": 2,
        "section": "6. Treatment Principles"
    },
    {
        "question": "What preventive measures can reduce the risk of malaria?",
        "answer": "Prevention includes avoiding mosquito bites, using insecticide-treated bed nets, wearing protective clothing, using effective mosquito repellents, reducing mosquito exposure, and using appropriate malaria chemoprophylaxis when indicated.",
        "page": 2,
        "section": "7. Prevention"
    },
    {
        "question": "What is the main clinical difference between P. falciparum and P. vivax?",
        "answer": "P. falciparum has the greatest association with severe malaria and death, while P. vivax can form dormant liver hypnozoites that may reactivate and cause relapses.",
        "page": 2,
        "section": "8. Key Species Comparison"
    },
    {
        "question": "Which Plasmodium species can cause relapse because of dormant liver stages?",
        "answer": "P. vivax and P. ovale can cause relapse because they can form dormant liver stages called hypnozoites.",
        "page": 2,
        "section": "8. Key Species Comparison"
    },
    {
        "question": "What is an important clinical characteristic of P. knowlesi malaria?",
        "answer": "P. knowlesi is a zoonotic malaria associated especially with Southeast Asia. It can progress rapidly and may resemble P. falciparum clinically.",
        "page": 2,
        "section": "8. Key Species Comparison"
    },
    {
        "question": "A patient has malaria with altered consciousness and acute kidney injury. How should this case be interpreted?",
        "answer": "The patient should be considered to have severe malaria because altered consciousness and acute kidney injury are important manifestations of severe disease. Severe malaria is a medical emergency requiring urgent treatment.",
        "page": 2,
        "section": "4. Severe Malaria"
    },
    {
        "question": "A patient develops malaria symptoms months after treatment for P. vivax. What could explain the recurrence?",
        "answer": "The recurrence may be caused by reactivation of dormant hypnozoites in the liver. P. vivax can form hypnozoites that reactivate later and cause relapses.",
        "page": 1,
        "section": "2. Transmission and Life Cycle"
    },
    {
        "question": "A patient has a strong clinical suspicion of malaria but the first diagnostic test is negative. What should be considered?",
        "answer": "Malaria should not necessarily be excluded after a single negative test when clinical suspicion remains high. Repeat testing may be required depending on the clinical situation and local diagnostic guidance.",
        "page": 2,
        "section": "5. Diagnosis"
    },
    {
        "question": "Why is geographic location important when selecting malaria treatment?",
        "answer": "Geographic location where the infection was acquired matters because local drug resistance patterns can influence which antimalarial treatment is appropriate.",
        "page": 2,
        "section": "6. Treatment Principles"
    }
]

    evaluate_with_ranx(test_cases, k=4)