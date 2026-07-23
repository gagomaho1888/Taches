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

    // --- Hamburger menu ---
    var hamburgerBtn = document.getElementById("hamburger-btn");
    var hamburgerDropdown = document.getElementById("hamburger-dropdown");
    if (hamburgerBtn && hamburgerDropdown) {
        hamburgerBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            hamburgerBtn.classList.toggle("open");
            hamburgerDropdown.classList.toggle("open");
        });
        document.addEventListener("click", (e) => {
            if (!hamburgerDropdown.contains(e.target) && !hamburgerBtn.contains(e.target)) {
                hamburgerBtn.classList.remove("open");
                hamburgerDropdown.classList.remove("open");
            }
        });
        hamburgerDropdown.querySelectorAll(".dropdown-item, a.dropdown-item").forEach(function(el) {
            el.addEventListener("click", function() {
                hamburgerBtn.classList.remove("open");
                hamburgerDropdown.classList.remove("open");
            });
        });
    }

    // --- Narrator ---
    function isNarratorEnabled() {
        return localStorage.getItem("narrator_enabled") === "true";
    }

    function speak(text) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "fr-FR";
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
    }

    var narratorBtn = document.getElementById("narrator-toggle");
    if (narratorBtn) {
        if (isNarratorEnabled()) {
            narratorBtn.classList.add("active");
        }
        narratorBtn.addEventListener("click", () => {
            var enabled = !isNarratorEnabled();
            localStorage.setItem("narrator_enabled", enabled);
            narratorBtn.classList.toggle("active", enabled);
            var banner = document.getElementById("narrator-banner");
            if (banner) {
                banner.style.display = enabled ? "flex" : "none";
            }
        });
    }

    var narratorBanner = document.getElementById("narrator-banner");
    if (narratorBanner && isNarratorEnabled()) {
        narratorBanner.style.display = "flex";
    }

    var narratorPlay = document.getElementById("narrator-play");
    if (narratorPlay) {
        narratorPlay.addEventListener("click", () => {
            speak(narratorPlay.dataset.title);
        });
    }

    var narratorDismiss = document.getElementById("narrator-dismiss");
    if (narratorDismiss) {
        narratorDismiss.addEventListener("click", () => {
            narratorDismiss.closest(".narrator-banner").style.display = "none";
        });
    }

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

    function getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : getCookie("csrftoken");
    }

    document.querySelectorAll(".task-toggle input[type='checkbox']").forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
            const taskId = this.dataset.taskId;
            const toggleUrl = "/taches/" + taskId + "/toggle-status/";
            const item = this.closest(".task-item, .task-card");
            const input = this;
            const intendedChecked = input.checked;

            input.disabled = true;

            fetch(toggleUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then((resp) => {
                    if (!resp.ok) throw new Error("Erreur serveur");
                    return resp.json();
                })
                .then((data) => {
                    if (data.ok) {
                        const isDone = data.new_status === "done" || data.new_status === "cancelled";

                        input.checked = isDone;

                        if (item) {
                            item.classList.toggle("completed-toggle", isDone);

                            const statusDot = item.querySelector(".task-status");
                            if (statusDot) {
                                statusDot.className = "task-status status-" + data.new_status;
                            }
                        }
                    }
                })
                .catch(() => {
                    input.checked = !intendedChecked;
                })
                .finally(() => {
                    input.disabled = false;
                });
        });
    });
});
