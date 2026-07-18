document.addEventListener("DOMContentLoaded", () => {
    const bars = document.querySelectorAll(".bar-fill");
    bars.forEach((bar) => {
        const width = bar.style.width;
        bar.style.width = "0%";
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                bar.style.width = width;
            });
        });
    });

    const statCards = document.querySelectorAll(".stat-card");
    statCards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(12px)";
        setTimeout(() => {
            card.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 80);
    });

    const toggle = document.getElementById("theme-toggle");
    if (toggle) {
        toggle.addEventListener("click", () => {
            const html = document.documentElement;
            const current = html.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            html.setAttribute("data-theme", next);
            localStorage.setItem("theme", next);
        });
    }

    // Block past deadline on client side
    const taskForm = document.querySelector("form.task-form");
    if (taskForm) {
        taskForm.addEventListener("submit", function(e) {
            const deadlineInput = document.getElementById("id_deadline");
            if (deadlineInput && deadlineInput.value) {
                const deadline = new Date(deadlineInput.value);
                const now = new Date();
                if (deadline < now) {
                    e.preventDefault();
                    alert("L'échéance ne peut pas être dans le passé.");
                }
            }
        });
    }

    // Auto-dismiss flash messages
    const alerts = document.querySelectorAll(".messages .alert");
    alerts.forEach((alert) => {
        alert.style.cursor = "pointer";
        alert.addEventListener("click", () => {
            alert.style.transition = "opacity 0.3s ease";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 300);
        });
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });
});
