# routes/teller_routes.py
from flask import Blueprint, request, jsonify, current_app
from services.gemma_service import ask_gemma
from services.db_service import get_customer_info
from config import Config
from utils.helpers import (
    clean_text,
    validate_language,
    validate_pdf_path,
    enforce_rate_limit,
    sanitize_output,
)
import logging

teller_bp = Blueprint("teller", __name__)

@teller_bp.route("/ask", methods=["POST"])
def ask_question():
    """
    Handles user questions for Eny-teller.
    Combines AI rules, optional PDF content, customer info, and memory.
    """
    try:
        client_id = request.remote_addr or "anonymous"
        if not enforce_rate_limit(client_id):
            return jsonify({"error": "Too many requests"}), 429

        data = request.get_json(silent=True) or {}
        question_raw = data.get("question")
        user_id = data.get("user_id")
        pdf_raw = data.get("pdf_path")  # Optional PDF path for context
        language_raw = data.get("language")  # Optional hint for multilingual responses

        question = clean_text(question_raw, Config.MAX_QUESTION_LENGTH)
        language = validate_language(language_raw)

        # --- 1. Validate input ---
        if not question:
            return jsonify({"error": "Missing question"}), 400

        try:
            pdf_path = validate_pdf_path(pdf_raw)
        except FileNotFoundError as err:
            return jsonify({"error": "PDF not found", "detail": str(err)}), 404
        except ValueError as err:
            return jsonify({"error": "Invalid PDF", "detail": str(err)}), 400

        if user_id is not None and not isinstance(user_id, (int, str)):
            return jsonify({"error": "Invalid user_id"}), 400

        # --- 2. Fetch user info from DB ---
        customer_info = {}
        if user_id is not None:
            customer_info = get_customer_info(user_id) or {}
            if isinstance(customer_info, dict):
                for key, value in list(customer_info.items()):
                    if isinstance(value, str):
                        customer_info[key] = clean_text(value, Config.MAX_CUSTOMER_INFO_LENGTH)
            else:
                customer_info = {}

        # --- 3. Combine context with question ---
        context_parts = [f"Question: {question}"]
        if customer_info:
            context_parts.append(f"Customer info: {customer_info}")
        if language:
            context_parts.append(f"Language hint: {language}")
        context_question = " \n".join(context_parts)

        # --- 4. Ask Eny-teller ---
        answer = ask_gemma(context_question, pdf_path=pdf_path)
        answer = sanitize_output(answer)

        # --- 5. Log unanswered questions ---
        if "not certain" in answer.lower():
            logging.info(f"Unanswered question stored for review: {question}")

        # --- 6. Return response ---
        return jsonify({"answer": answer})

    except Exception as e:
        logging.error(f"Error in /ask route: {e}")
        return jsonify({"error": "Internal server error"}), 500
