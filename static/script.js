document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("resumeForm");
    const fileInput = document.getElementById("resumeUpload");
    const jobDescription = document.getElementById("jobDescription");
    const loadingDiv = document.getElementById("loading");
    const resultsContent = document.getElementById("resultsContent");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        if (fileInput.files.length === 0) {
            alert("Please upload a resume file.");
            return;
        }

        // Hide results and show loading
        resultsContent.style.display = "none";
        loadingDiv.style.display = "block";

        const formData = new FormData();
        formData.append("resume", fileInput.files[0]);
        formData.append("job_description", jobDescription.value);

        fetch("/analyze_resume", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingDiv.style.display = "none";
            resultsContent.style.display = "block";

            if (data.error) {
                resultsContent.innerHTML = `<div class="analysis-card"><p class="error">Error: ${data.error}</p></div>`;
                return;
            }

            // Extract data
            const styleIssues = data.style_issues || [];
            const lineAnalysis = data.line_analysis || [];
            const formattingFeedback = data.formatting_feedback || [];
            const missingKeywords = data.missing_keywords || [];
            const atsScore = data.score || 0;
            const feedback = data.feedback || "No feedback available";

            // 1) Score & Overall Feedback card
            const scoreCard = `
              <div class="score-display">
                <h3>ATS COMPATIBILITY SCORE</h3>
                <div class="score-value">${atsScore}</div>
                <p>${feedback}</p>
              </div>
            `;

            // 2) Missing Keywords card
            const missingCard = `
              <div class="analysis-section">
                <h3 class="section-title">KEYWORD ANALYSIS</h3>
                <div class="analysis-card">
                  <h4 class="card-title">${missingKeywords.length > 0 ? "MISSING KEYWORDS" : "KEYWORD MATCH"}</h4>
                  <div class="card-content">
                    ${
                      missingKeywords.length > 0
                      ? `
                        <p>These important keywords from the job description are missing from your resume:</p>
                        <div class="keyword-list">
                          ${missingKeywords.map(kw => `<span class="keyword">${kw}</span>`).join("")}
                        </div>
                        `
                      : `<p>✅ All important keywords matched!</p>`
                    }
                  </div>
                </div>
              </div>
            `;

            // 3) Bullet-by-Bullet Analysis
            let bulletAnalysisHtml = "";
            if (styleIssues.length > 0) {
                bulletAnalysisHtml += `
                    <p><strong>Style Issues:</strong></p>
                    <ul>
                        ${styleIssues.map(issue => `<li>⚠️ ${issue}</li>`).join("")}
                    </ul>
                `;
            }

            if (lineAnalysis.length > 0) {
                bulletAnalysisHtml += `
                    <div class="analysis-section">
                      <h3 class="section-title">CONTENT SUGGESTIONS</h3>
                      ${lineAnalysis.map(entry => {
                          // Grammar block
                          let grammarHtml;
                          if (entry.grammar_errors && entry.grammar_errors.length > 0) {
                              grammarHtml = `
                                <div class="suggestion-item">
                                  <p><strong>Grammar Issues:</strong></p>
                                  <ul>
                                    ${entry.grammar_errors.map(err => `
                                      <li>⚠️ ${err.message || err}</li>
                                    `).join("")}
                                  </ul>
                                </div>
                              `;
                          } else {
                              grammarHtml = `<p>✅ No grammar issues found.</p>`;
                          }

                          // Improved text
                          const improvedBlock = `
                            <div class="suggestion-item">
                              <p><strong>Original:</strong> ${entry.text}</p>
                              <p><strong>Improved:</strong> ${entry.paraphrased || "<i>No suggestion available</i>"}</p>
                            </div>
                          `;

                          return `
                            <div class="analysis-card">
                              ${grammarHtml}
                              ${improvedBlock}
                            </div>
                          `;
                      }).join("")}
                    </div>
                `;
            }

            // 4) Formatting Issues card
            const formattingCard = `
              <div class="analysis-section">
                <h3 class="section-title">FORMATTING ANALYSIS</h3>
                <div class="analysis-card">
                  <h4 class="card-title">${formattingFeedback.length > 0 ? "FORMATTING ISSUES" : "FORMATTING"}</h4>
                  <div class="card-content">
                  ${
                    formattingFeedback.length > 0
                    ? `
                      <ul>
                        ${formattingFeedback.map(fb => `<li>${fb}</li>`).join("")}
                      </ul>
                      `
                    : `<p>✅ Perfect formatting!</p>`
                  }
                  </div>
                </div>
              </div>
            `;

            // Final output
            resultsContent.innerHTML = `
              ${scoreCard}
              ${missingCard}
              ${bulletAnalysisHtml}
              ${formattingCard}
            `;
        })
        .catch(err => {
            loadingDiv.style.display = "none";
            resultsContent.style.display = "block";
            resultsContent.innerHTML = `
              <div class="analysis-card">
                <p class="error">Error: Something went wrong. Please try again.</p>
              </div>
            `;
            console.error(err);
        });
    });
});