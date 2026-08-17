/* ScamShield "Can You Spot The Scam?" Interactive Quiz Engine */

let currentQuestionIndex = 0;
let quizQuestions = [];
let userScore = 0;

function loadQuizQuestions() {
    const container = document.getElementById('quizContainer');
    if (!container) return;

    fetch('/api/quiz/questions')
        .then(res => res.json())
        .then(data => {
            quizQuestions = data.questions;
            currentQuestionIndex = 0;
            userScore = 0;
            renderCurrentQuestion();
        })
        .catch(err => {
            if (container) container.innerHTML = '<p class="text-danger">Failed to load quiz questions.</p>';
        });
}

function renderCurrentQuestion() {
    const container = document.getElementById('quizContainer');
    if (!container || !quizQuestions.length) return;

    if (currentQuestionIndex >= quizQuestions.length) {
        renderQuizSummary();
        return;
    }

    const q = quizQuestions[currentQuestionIndex];
    const progressPercent = ((currentQuestionIndex + 1) / quizQuestions.length) * 100;

    let optionsHtml = '';
    q.options.forEach((opt, idx) => {
        optionsHtml += `
            <button class="quiz-option-btn" onclick="submitQuizAnswer(${idx}, ${opt.is_correct})">
                <span class="option-letter">${String.fromCharCode(65 + idx)}</span>
                <span class="option-text">${opt.text}</span>
            </button>
        `;
    });

    container.innerHTML = `
        <div class="glass-card quiz-card">
            <div class="quiz-header">
                <span class="badge-risk badge-verify">Question ${currentQuestionIndex + 1} of ${quizQuestions.length}</span>
                <span class="quiz-difficulty">Difficulty: <strong>${q.difficulty}</strong></span>
            </div>
            <div class="progress-bar-container" style="background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px; margin: 1rem 0;">
                <div class="progress-fill" style="width: ${progressPercent}%; background: var(--accent-cyan); height: 100%; border-radius: 3px; transition: width 0.3s;"></div>
            </div>
            <h3 class="quiz-question-title" style="margin: 1.5rem 0;">${q.question}</h3>
            <div class="quiz-options-grid" style="display: flex; flex-direction: column; gap: 0.85rem;">
                ${optionsHtml}
            </div>
            <div id="quizFeedbackBox" class="quiz-feedback-box" style="display: none; margin-top: 1.5rem; padding: 1.25rem; border-radius: var(--radius-md);"></div>
        </div>
    `;
}

function submitQuizAnswer(selectedIndex, isCorrect) {
    const feedbackBox = document.getElementById('quizFeedbackBox');
    const optionBtns = document.querySelectorAll('.quiz-option-btn');
    
    // Disable all options once answered
    optionBtns.forEach(btn => btn.disabled = true);
    
    if (isCorrect) {
        userScore++;
        optionBtns[selectedIndex].classList.add('correct');
        feedbackBox.style.display = 'block';
        feedbackBox.style.background = 'rgba(16, 185, 129, 0.15)';
        feedbackBox.style.border = '1px solid rgba(16, 185, 129, 0.4)';
        feedbackBox.innerHTML = `
            <h4 style="color: var(--risk-safe);"><i class="fas fa-check-circle"></i> Spot On! Correct Answer</h4>
            <p style="margin-top: 0.5rem;">${quizQuestions[currentQuestionIndex].explanation}</p>
            <button class="btn btn-primary btn-sm" style="margin-top: 1rem;" onclick="nextQuestion()">Next Question <i class="fas fa-arrow-right"></i></button>
        `;
    } else {
        optionBtns[selectedIndex].classList.add('wrong');
        feedbackBox.style.display = 'block';
        feedbackBox.style.background = 'rgba(239, 68, 68, 0.15)';
        feedbackBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
        feedbackBox.innerHTML = `
            <h4 style="color: var(--risk-high);"><i class="fas fa-times-circle"></i> Scam Alert! That Choice puts you at risk</h4>
            <p style="margin-top: 0.5rem;">${quizQuestions[currentQuestionIndex].explanation}</p>
            <button class="btn btn-primary btn-sm" style="margin-top: 1rem;" onclick="nextQuestion()">Next Question <i class="fas fa-arrow-right"></i></button>
        `;
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    renderCurrentQuestion();
}

function renderQuizSummary() {
    const container = document.getElementById('quizContainer');
    const accuracy = Math.round((userScore / quizQuestions.length) * 100);

    // Submit quiz results to server to update user awareness score
    fetch('/api/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ score: userScore, total: quizQuestions.length, accuracy: accuracy })
    })
    .then(res => res.json())
    .then(data => {
        if (data.new_awareness_score) {
            showToast(`Awareness Score Updated: ${data.new_awareness_score}/100 🛡️`, 'success');
        }
    })
    .catch(err => console.error(err));

    container.innerHTML = `
        <div class="glass-card text-center" style="padding: 3rem 2rem;">
            <div style="font-size: 3.5rem; color: var(--accent-cyan); margin-bottom: 1rem;"><i class="fas fa-award"></i></div>
            <h2>Quiz Complete!</h2>
            <p>Your Scam Awareness Score for this session:</p>
            <div style="font-size: 3.5rem; font-weight: 800; color: var(--text-primary); margin: 1rem 0;">${accuracy}%</div>
            <p>You correctly spotted <strong>${userScore}</strong> out of <strong>${quizQuestions.length}</strong> scam scenarios.</p>
            <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center;">
                <button class="btn btn-primary" onclick="loadQuizQuestions()"><i class="fas fa-redo"></i> Retake Quiz</button>
                <a href="/safety-center" class="btn btn-secondary"><i class="fas fa-shield-alt"></i> Read Safety Guides</a>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', loadQuizQuestions);
