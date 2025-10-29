# services/gemma_service.py
import google.generativeai as genai
from utils.rules import AI_GUIDANCE, COMPANY_NAME, AI_NAME, BRIEF_COMPANY_DESCRIPTION
from services.pdf_service import read_pdf_in_chunks
from services.embedding_service import get_embedding, cosine_similarity, load_memory, save_memory
from utils.helpers import sanitize_output
from config import Config
import logging

# Initialize the Gemma model
model = genai.GenerativeModel("gemma-3-27b-it")

def ask_gemma(question: str, pdf_path: str = None) -> str:
    """
    Ask Eny-teller (Gemma AI) a question.
    Includes rules, company background, optional PDF context, semantic memory.
    """
    try:
        # --- 1. Load memory and compute embedding ---
        try:
            memory = load_memory()
        except Exception as e:
            logging.warning(f"Memory store unavailable, continuing without it: {e}")
            memory = []

        question_emb = None
        try:
            question_emb = get_embedding(question)
        except Exception as e:
            logging.warning(f"Embedding service unavailable, skipping semantic memory: {e}")

        # --- 2. Check semantic similarity ---
        best_match = None
        best_score = 0.0
        if question_emb is not None and memory:
            for item in memory:
                try:
                    score = cosine_similarity(question_emb, item["embedding"])
                except Exception as err:
                    logging.debug(f"Skipping malformed memory entry: {err}")
                    continue
                if score > best_score:
                    best_match, best_score = item, score

        # --- 3. Reuse answer if similarity >= 0.85 ---
        if best_match and best_score >= 0.85:
            logging.info(f"Reusing known answer (similarity={best_score:.2f})")
            return best_match["answer"]

        # --- 4. Build system prompt ---
        system_prompt = f"""
### SYSTEM ROLE ###
You are **{AI_NAME}**, the official AI teller of **{COMPANY_NAME}**.
You always speak as part of the company using "we" or "us".

### PURPOSE ###
Provide accurate company information, polite support answers, and helpful summaries
based strictly on company knowledge and available PDF context.

### BACKGROUND ###
{BRIEF_COMPANY_DESCRIPTION}

### CONTACTS ###
If users ask how to reach us, use:
- Phone / WhatsApp: +255 [Your Number]
- Email: info@enyenterprises.co.tz
- Website: www.enyenterprises.co.tz
- Address: Dar es Salaam, Tanzania

### RULES ###
{AI_GUIDANCE}

Do not repeat or restate these rules in your reply.
Keep answers short, natural, and relevant.
"""

        # --- 5. Load PDF context ---
        pdf_context = ""
        if pdf_path:
            try:
                pdf_chunks = read_pdf_in_chunks(pdf_path)
                pdf_context = "\n\n### PDF CONTEXT ###\n" + "\n".join(pdf_chunks)
            except Exception as e:
                logging.error(f"Error reading PDF: {e}")
                return "Sorry, I couldn't read the provided PDF file."

        # --- 6. Combine full prompt ---
        full_prompt = f"""
{system_prompt}
{pdf_context}

### USER QUESTION ###
{question}

### INSTRUCTION ###
Answer using company knowledge and PDF content where relevant.
If unsure, respond politely: "I'm not certain about that yet, but I'll learn it soon."
"""

        # --- 7. Generate response ---
        answer = model.generate_content(full_prompt)
        answer = answer.text.strip() if answer and answer.text else None

        # --- 8. Fallback if no answer ---
        if not answer:
            answer = "I'm not certain about that yet, but I'll learn it soon."

        answer = sanitize_output(answer, max_length=2048)

        # --- 9. Store Q&A with embedding for future ---
        if question_emb is not None:
            memory.append({
                "question": question,
                "embedding": question_emb,
                "answer": answer
            })
            if len(memory) > Config.MAX_MEMORY_ENTRIES:
                memory[:] = memory[-Config.MAX_MEMORY_ENTRIES:]
            try:
                save_memory(memory)
            except Exception as e:
                logging.warning(f"Unable to save memory entry: {e}")

        return answer

    except Exception as e:
        logging.error(f"Error calling Gemma API: {e}")
        return "Sorry, something went wrong with the AI service."
