from flask import Flask, request, jsonify, render_template
import os
import re
from pathlib import Path

# Keep these imports
from utils.text_processing import extract_text, preprocess_text, rank_resume
from utils.formatting import analyze_pdf_formatting
# REMOVE the grouping import (was used for content organization)
# from utils.grouping import get_hybrid_grouping_analysis
from utils.enhanced_grammar_and_paraphrasing import check_grammar_and_strength

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ACCOMPLISHMENT_KEYWORDS = r"\b(developed|implemented|created|improved|achieved|designed|optimized)\b"
RESULT_KEYWORDS = r"\b(\d+%|\d+\s*(?:points|percent)|increased|decreased|improved|resulted|reduced)\b"

@app.route("/")
def index():
    return render_template("index.html")

def is_experience_bullet(text):
    text_lower = text.lower()
    return (re.search(ACCOMPLISHMENT_KEYWORDS, text_lower)
            and re.search(RESULT_KEYWORDS, text_lower)
            and len(text.split()) >= 5)

@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    """
    1) Extract bullet lines from PDF/DOCX
    2) Group them so we can do grammar checks
    3) Analyze for ATS rank, formatting, grammar, etc.
    4) Return JSON WITHOUT 'Content Organization' or 'grouping_issues'
    """
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files["resume"]
    job_desc = request.form.get("job_description", "")

    if not job_desc:
        return jsonify({"error": "Job description required"}), 400

    # Save resume
    resume_path = Path(app.config["UPLOAD_FOLDER"]) / resume_file.filename
    resume_file.save(resume_path)

    try:
        # Step 1: Extract bullet-based text
        raw_text = extract_text(resume_path)

        # Step 2: Group bullet lines into paragraphs for grammar context
        grouped_lines = []
        current_para = []
        lines = raw_text.splitlines()

        for line in lines:
            stripped = line.strip()

            # If blank line -> end current paragraph
            if not stripped:
                if current_para:
                    grouped_lines.append(" ".join(current_para))
                    current_para = []
                continue

            # If line starts with a bullet symbol
            if stripped.startswith(("•", "-", "*")):
                # close existing paragraph if any
                if current_para:
                    grouped_lines.append(" ".join(current_para))
                    current_para = []
                # start a new bullet paragraph
                current_para.append(stripped)
            else:
                current_para.append(stripped)

        if current_para:
            grouped_lines.append(" ".join(current_para))

        grouped_text = "\n\n".join(grouped_lines)
        preprocessed_text = preprocess_text(grouped_text)

        # Export debug
        debug_path = Path(app.config["UPLOAD_FOLDER"]) / "grouped_output_debug.txt"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(grouped_text)
        print(f"[DEBUG] Grouped text written to {debug_path}")

        # Step 3: Analyze
        formatting_data = analyze_pdf_formatting(resume_path)
        keyword_results = rank_resume(preprocessed_text, preprocess_text(job_desc))

        # REMOVED: grouping_issues = get_hybrid_grouping_analysis(str(resume_path))[1]
        # because we no longer want Content Organization logic

        # Step 4: Grammar & bullet-based paraphrasing
        bullet_lines = []
        for para in grouped_lines:
            if para and para[0] in ("•", "-", "*"):
                bullet_text = para[1:].lstrip()
                bullet_lines.append(bullet_text)

        bullet_analysis = {}
        try:
            bullet_analysis = check_grammar_and_strength("\n".join(bullet_lines))
        except Exception as e:
            print(f"Error in grammar and strength analysis: {e}")
            bullet_analysis = {"style_issues": [], "line_analysis": [], "metrics": {}}

        # Step 5: Build final JSON (no grouping_issues)
        return jsonify({
            "score": keyword_results.get("score", 0),
            "missing_keywords": keyword_results.get("missing_keywords", []),
            "formatting_feedback": format_formatting_results(formatting_data),
            # "grouping_issues": grouping_issues,  <-- REMOVED
            "feedback": keyword_results.get("feedback", "No feedback available"),
            "style_issues": bullet_analysis.get("style_issues", []),
            "line_analysis": bullet_analysis.get("line_analysis", []),
            "metrics": bullet_analysis.get("metrics", {})
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def format_formatting_results(formatting_data):
    messages = []

    if formatting_data.get("unique_font_names", 0) > 3:
        messages.append(
            f"Too many different fonts ({formatting_data['unique_font_names']}) - use 2-3 maximum."
        )
    if formatting_data.get("bullet_percentage", 0) < 30:
        messages.append(
            f"Low bullet usage ({formatting_data['bullet_percentage']}%) - Increase to ~40% or more for clarity."
        )

    bullet_consistency_msg = formatting_data.get("bullet_font_consistency")
    if bullet_consistency_msg:
        messages.append(f"[Bullet Font Check] {bullet_consistency_msg}")

    return messages

if __name__ == "__main__":
    print("Loading ML models...")
    app.run(host="0.0.0.0", port=5001, debug=True)
