document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      // helper to escape HTML
      function escapeHtml(str) {
        return String(str)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }

      // reset activity select options
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants HTML
        let participantsHTML = "";
        if (Array.isArray(details.participants) && details.participants.length > 0) {
          const items = details.participants
            .map(
              (p) =>
                `<li><span class="participant-email">${escapeHtml(p)}</span><button class="participant-delete" data-email="${escapeHtml(
                  p
                )}" title="Remove participant">✖</button></li>`
            )
            .join("");
          participantsHTML = `
            <div class="participants" data-activity="${escapeHtml(name)}">
              <strong>Participants:</strong>
              <ul>${items}</ul>
            </div>
          `;
        } else {
          participantsHTML = `
            <div class="participants empty" data-activity="${escapeHtml(name)}"><em>No participants yet</em></div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "message success";
        signupForm.reset();
        // refresh activities to show new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "message error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "message error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
      fetchActivities();

      // Delegate click for delete participant buttons
      activitiesList.addEventListener("click", async (e) => {
        const btn = e.target.closest(".participant-delete");
        if (!btn) return;

        const email = btn.dataset.email;
        // find activity name from closest participants container
        const participantsDiv = btn.closest(".participants");
        const activityName = participantsDiv && participantsDiv.dataset.activity;
        if (!activityName || !email) return;

        if (!confirm(`Remove ${email} from ${activityName}?`)) return;

        try {
          const res = await fetch(
            `/activities/${encodeURIComponent(activityName)}/participants`,
            {
              method: "DELETE",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email }),
            }
          );
          const data = await res.json();
          if (res.ok) {
            messageDiv.textContent = data.message;
            messageDiv.className = "message success";
            messageDiv.classList.remove("hidden");
            // refresh list
            fetchActivities();
          } else {
            messageDiv.textContent = data.detail || "Failed to remove participant";
            messageDiv.className = "message error";
            messageDiv.classList.remove("hidden");
          }
          setTimeout(() => messageDiv.classList.add("hidden"), 4000);
        } catch (err) {
          console.error(err);
        }
      });
});
