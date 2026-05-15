
// ============================================================
// admin.js — Admin Panel JavaScript
// Runs on: admin pages
// Purpose: small UI helpers for the admin panel
// ============================================================

// ── Auto-dismiss flash messages after 4 seconds ──────────────
document.addEventListener("DOMContentLoaded", function () {
  const flashMessages = document.querySelectorAll(".flash");  // All flash messages

  flashMessages.forEach(function (msg) {
    // After 4 seconds, fade out and remove the flash message automatically
    setTimeout(function () {
      msg.style.transition = "opacity 0.5s";  // Smooth fade out
      msg.style.opacity    = "0";

      // Remove from DOM after fade completes
      setTimeout(function () {
        msg.remove();
      }, 500);
    }, 4000);  // 4000ms = 4 seconds before fade starts
  });
});
