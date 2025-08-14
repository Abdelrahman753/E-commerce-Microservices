// DOM elements
const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginBtn = document.getElementById("login-btn");
const btnText = document.querySelector(".btn-text");
const btnLoading = document.querySelector(".btn-loading");
const errorMessage = document.getElementById("error-message");

// Check if user is already logged in
document.addEventListener("DOMContentLoaded", () => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser"));
    const isLoginPage = window.location.pathname.includes("login.html");

    if (currentUser && currentUser.access_token && !isLoginPage) {
        window.location.href = "index.html";
    }
});

// Form submission
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    // Basic validation
    if (!email || !password) {
        showError("يرجى ملء جميع الحقول");
        return;
    }

    if (!isValidEmail(email)) {
        showError("يرجى إدخال بريد إلكتروني صحيح");
        return;
    }

    await handleLogin(email, password);
});

// Handle login
async function handleLogin(email, password) {
    try {
        setLoading(true);
        hideError();

        const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Store user data (token + id)
            localStorage.setItem("currentUser", JSON.stringify({
                user_id: data.user_id,
                access_token: data.access_token
            }));

            // Redirect to home page
            window.location.href = "index.html";
        } else {
            showError(data.error || data.message || "حدث خطأ في تسجيل الدخول");
        }
    } catch (error) {
        console.error("Login error:", error);
        showError("تعذر الاتصال بالخادم. حاول مرة أخرى.");
    } finally {
        setLoading(false);
    }
}

// Utility functions
function setLoading(loading) {
    loginBtn.disabled = loading;
    btnText.style.display = loading ? "none" : "inline";
    btnLoading.style.display = loading ? "inline" : "none";
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";

    emailInput.classList.add("error");
    passwordInput.classList.add("error");

    setTimeout(() => {
        emailInput.classList.remove("error");
        passwordInput.classList.remove("error");
    }, 3000);
}

function hideError() {
    errorMessage.style.display = "none";
    emailInput.classList.remove("error");
    passwordInput.classList.remove("error");
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Clear errors when typing
emailInput.addEventListener("input", hideError);
passwordInput.addEventListener("input", hideError);
