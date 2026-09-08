/**
 * Main Application Controller for Agricultural Disease Observation App.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation Tabs
  const navTabs = document.querySelectorAll(".nav-tab");
  const views = document.querySelectorAll(".view-panel");

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetView = tab.dataset.view;

      navTabs.forEach(t => t.classList.remove("active"));
      views.forEach(v => v.classList.remove("active"));

      tab.classList.add("active");
      const activePanel = document.getElementById(targetView);
      if (activePanel) activePanel.classList.add("active");

      // Trigger lazy view loads
      if (targetView === "view-officer") {
        OfficerDashboard.fetchMetrics();
        OfficerDashboard.fetchCases();
      } else if (targetView === "view-expert") {
        ExpertStation.fetchPendingCases();
      }
    });
  });

  // Initialize Modules
  if (typeof FarmerWizard !== "undefined") FarmerWizard.init();
  if (typeof OfficerDashboard !== "undefined") OfficerDashboard.init();
  if (typeof ExpertStation !== "undefined") ExpertStation.init();

  // Reset Demo Data Button
  const resetBtn = document.getElementById("btn-reset-demo");
  if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
      if (confirm("Reset demo cases back to default 12 benchmark cases?")) {
        try {
          resetBtn.innerText = "Resetting...";
          const res = await fetch("/api/cases"); // trigger or seed
          location.reload();
        } catch (err) {
          alert("Reset failed: " + err.message);
        }
      }
    });
  }
});
