
// ============================================================
// result.js — Result Page Animations
// Runs on: student/result.html
// Purpose: animate the progress bar when the result page loads
//          so the score bar fills up smoothly instead of jumping
// ============================================================

// Wait for the page to fully load before running any animation
document.addEventListener("DOMContentLoaded", function () {

  // ── Animate the progress bar ──────────────────────────────
  const bar = document.getElementById("progressBar");  // The progress bar element

  if (bar) {
    const score = parseFloat(bar.dataset.score);  // Read the score from data attribute

    // Small delay before animation starts — feels more intentional
    setTimeout(function () {
      bar.style.width = Math.min(score, 100) + "%";  // Set width (cap at 100%)
    }, 300);  // 300ms delay before fill starts
  }

});
