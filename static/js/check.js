
// ============================================================
// check.js — Live Word Counter for the Idea Submission Form
// Runs on: student/check.html
// Purpose: count words in title and description in real-time
//          and show color-coded feedback to guide the student
// ============================================================

// ── Helper: count words in a string ──────────────────────────
// Splits text by spaces and filters out empty strings
function countWords(text) {
  return text.trim().split(/\s+/).filter(word => word.length > 0).length;
}

// ── Title word counter ────────────────────────────────────────
const titleInput   = document.getElementById("title");       // Title input field
const titleCounter = document.getElementById("titleCounter"); // Counter display element

if (titleInput && titleCounter) {
  // Update the counter every time the user types in the title field
  titleInput.addEventListener("input", function () {
    const count = countWords(this.value);  // Count current words
    titleCounter.textContent = count + " words";

    // Change color based on whether count is in the valid range (5-15)
    titleCounter.className = "word-counter"; // Reset classes first
    if (count >= 5 && count <= 15) {
      titleCounter.classList.add("ok");       // Green — perfect
    } else if (count > 0 && count < 5) {
      titleCounter.classList.add("too-few");  // Red — too short
    } else if (count > 15) {
      titleCounter.classList.add("too-many"); // Orange — too long
    }
  });
}

// ── Description word counter ──────────────────────────────────
const descInput   = document.getElementById("description");   // Description textarea
const descCounter = document.getElementById("descCounter");   // Counter display element

if (descInput && descCounter) {
  // Update the counter every time the user types in the description
  descInput.addEventListener("input", function () {
    const count = countWords(this.value);  // Count current words
    descCounter.textContent = count + " / 50–200 words";

    // Change color based on whether count is in the valid range (50-200)
    descCounter.className = "word-counter"; // Reset classes first
    if (count >= 50 && count <= 200) {
      descCounter.classList.add("ok");       // Green — perfect range
    } else if (count > 0 && count < 50) {
      descCounter.classList.add("too-few");  // Red — not enough detail
    } else if (count > 200) {
      descCounter.classList.add("too-many"); // Orange — too long
    }
  });
}

// ── Form submission validation ────────────────────────────────
// Prevent form from being submitted if word counts are wrong
const checkForm  = document.getElementById("checkForm");
const submitBtn  = document.getElementById("submitBtn");

if (checkForm) {
  checkForm.addEventListener("submit", function (e) {
    const titleWords = countWords(titleInput.value);       // Count title words
    const descWords  = countWords(descInput.value);        // Count description words

    // Validate title length
    if (titleWords < 5 || titleWords > 15) {
      e.preventDefault();  // Stop form from submitting
      alert("Please make sure your title is between 5 and 15 words.");
      titleInput.focus();  // Bring cursor back to title field
      return;
    }

    // Validate description length
    if (descWords < 50) {
      e.preventDefault();  // Stop form from submitting
      alert("Your description is too short. Please write at least 50 words.");
      descInput.focus();   // Bring cursor back to description field
      return;
    }

    if (descWords > 300) {
      e.preventDefault();
      alert("Your description is too long. Please keep it under 300 words.");
      descInput.focus();
      return;
    }

    // If all validations pass, show loading state on the button
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    submitBtn.disabled = true;  // Prevent double-clicking
  });
}
