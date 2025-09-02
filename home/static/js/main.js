document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("nav ul li a").forEach(link => {
        link.addEventListener("click", function (e) {
            const target = this.getAttribute("href");
            if (target.startsWith("#")) {
                e.preventDefault();
                document.querySelector(target).scrollIntoView({
                    behavior: "smooth"
                });
            }
        });
    });

    // Get Started button → scroll to features
    const getStartedBtn = document.querySelector(".hero button");
    if (getStartedBtn) {
        getStartedBtn.addEventListener("click", function () {
            const featuresSection = document.querySelector(".features");
            if (featuresSection) {
                featuresSection.scrollIntoView({ behavior: "smooth" });
            }
        });
    }

    // Highlight feature cards on hover
    const featureCards = document.querySelectorAll(".feature-card");
    featureCards.forEach(card => {
        card.addEventListener("mouseenter", () => {
            card.style.boxShadow = "0 12px 25px rgba(78, 115, 223, 0.35)";
        });
        card.addEventListener("mouseleave", () => {
            card.style.boxShadow = "0 4px 10px rgba(0,0,0,0.1)";
        });
    });

    // Fake Login/Signup action (demo)
    const navLinks = document.querySelectorAll("nav ul li a");
    const loginLink = navLinks[2];  // 3rd link
    const signupLink = navLinks[3]; // 4th link

    if (loginLink) {
        loginLink.addEventListener("click", (e) => {
            e.preventDefault();
            alert("🔑 Login functionality coming soon!");
        });
    }

    if (signupLink) {
        signupLink.addEventListener("click", (e) => {
            e.preventDefault();
            alert("📝 Signup functionality coming soon!");
        });
    }
});