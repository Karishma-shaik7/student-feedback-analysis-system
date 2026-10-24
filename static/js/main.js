/**
 * Student Feedback Analysis System - Frontend Interactions
 * Vanilla JavaScript: Star Rating, Form Debounce, Character Counter, Mobile Sidebar
 */

document.addEventListener("DOMContentLoaded", () => {
    initStarRating();
    initFeedbackFormValidation();
    initCommentCounter();
    initMobileSidebar();
    initDismissibleAlerts();
    initSubmissionCelebration();
});

/**
 * Interactive Star Rating with live description and hover states
 */
function initStarRating() {
    const starInputs = document.querySelectorAll('input[name="rating"]');
    const descriptor = document.getElementById("rating-descriptor");
    const starLabels = document.querySelectorAll(".star-label");

    if (!starInputs.length || !descriptor) return;

    const ratingDescriptions = {
        "1": "★☆☆☆☆ — 1 / 5 (Needs Significant Improvement)",
        "2": "★★☆☆☆ — 2 / 5 (Fair, Could Be Better)",
        "3": "★★★☆☆ — 3 / 5 (Good, Met Expectations)",
        "4": "★★★★☆ — 4 / 5 (Very Good, High Quality)",
        "5": "★★★★★ — 5 / 5 (Excellent, Exceeded Expectations!)"
    };

    function updateDescriptor(val) {
        if (ratingDescriptions[val]) {
            descriptor.textContent = ratingDescriptions[val];
            descriptor.style.color = "#fbbf24";
        } else {
            descriptor.textContent = "Select your rating (1 to 5 stars)";
            descriptor.style.color = "var(--text-muted)";
        }
    }

    // Check if a rating is already pre-selected
    const checkedRadio = document.querySelector('input[name="rating"]:checked');
    if (checkedRadio) {
        updateDescriptor(checkedRadio.value);
    }

    starInputs.forEach(radio => {
        radio.addEventListener("change", (e) => {
            updateDescriptor(e.target.value);
        });
    });

    // Hover feedback
    starLabels.forEach(label => {
        label.addEventListener("mouseenter", () => {
            const val = label.getAttribute("data-value");
            if (val) updateDescriptor(val);
        });

        label.addEventListener("mouseleave", () => {
            const currentChecked = document.querySelector('input[name="rating"]:checked');
            if (currentChecked) {
                updateDescriptor(currentChecked.value);
            } else {
                updateDescriptor(null);
            }
        });
    });
}

/**
 * Comment Character Counter
 */
function initCommentCounter() {
    const commentInput = document.getElementById("comment");
    const counterDisplay = document.getElementById("comment-counter");

    if (!commentInput || !counterDisplay) return;

    const maxLength = commentInput.getAttribute("maxlength") || 2000;

    commentInput.addEventListener("input", () => {
        const currentLength = commentInput.value.length;
        counterDisplay.textContent = `${currentLength} / ${maxLength} characters`;
        if (currentLength >= maxLength * 0.9) {
            counterDisplay.style.color = "var(--warning)";
        } else {
            counterDisplay.style.color = "var(--text-muted)";
        }
    });
}

/**
 * Client-Side Validation and Double-Submission Prevention
 */
function initFeedbackFormValidation() {
    const form = document.getElementById("feedback-form");
    const submitBtn = document.getElementById("submit-btn");

    if (!form || !submitBtn) return;

    form.addEventListener("submit", (e) => {
        const courseSelect = document.getElementById("course_id");
        const ratingChecked = document.querySelector('input[name="rating"]:checked');

        let isValid = true;
        let errorMessage = "";

        if (!courseSelect || !courseSelect.value) {
            isValid = false;
            errorMessage = "Please select a course from the dropdown catalog.";
            if (courseSelect) courseSelect.focus();
        } else if (!ratingChecked) {
            isValid = false;
            errorMessage = "Please choose a satisfaction rating (1 to 5 stars).";
            const firstStar = document.querySelector(".star-label");
            if (firstStar) firstStar.focus();
        }

        if (!isValid) {
            e.preventDefault();
            showClientAlert(errorMessage, "warning");
            return;
        }

        // Prevent accidental duplicate clicks
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
            </svg>
            Submitting Feedback...
        `;
    });
}

/**
 * Displays a non-blocking toast alert dynamically
 */
function showClientAlert(message, type = "warning") {
    let container = document.querySelector(".flash-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "flash-container";
        const main = document.querySelector(".content-container");
        if (main) main.insertBefore(container, main.firstChild);
    }

    const alert = document.createElement("div");
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>⚠️ ${message}</span>
        <button type="button" class="alert-close" aria-label="Close">&times;</button>
    `;

    container.appendChild(alert);

    alert.querySelector(".alert-close").addEventListener("click", () => {
        alert.remove();
    });

    setTimeout(() => {
        if (alert.parentNode) {
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 300);
        }
    }, 6000);
}

/**
 * Dismissible alert handler
 */
function initDismissibleAlerts() {
    document.querySelectorAll(".alert-close").forEach(button => {
        button.addEventListener("click", () => {
            const alert = button.closest(".alert");
            if (alert) {
                alert.style.opacity = "0";
                alert.style.transform = "translateY(-10px)";
                setTimeout(() => alert.remove(), 250);
            }
        });
    });
}

/**
 * Mobile Sidebar Drawer Toggle
 */
function initMobileSidebar() {
    const toggleBtn = document.getElementById("mobile-toggle");
    const sidebar = document.querySelector(".app-sidebar");

    if (!toggleBtn || !sidebar) return;

    toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });

    // Close when clicking outside on mobile
    document.addEventListener("click", (e) => {
        if (window.innerWidth <= 768 && sidebar.classList.contains("open")) {
            if (!sidebar.contains(e.target) && e.target !== toggleBtn) {
                sidebar.classList.remove("open");
            }
        }
    });
}

/**
 * Optional Celebration after feedback submission
 */
function initSubmissionCelebration() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("submitted") === "1") {
        // Clean URL to prevent re-triggering on refresh
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}
