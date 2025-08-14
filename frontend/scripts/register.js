// DOM elements
const registerForm = document.getElementById("register-form");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const phoneInput = document.getElementById("phone");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm-password");
const registerBtn = document.getElementById("register-btn");
const btnText = document.querySelector(".btn-text");
const btnLoading = document.querySelector(".btn-loading");
const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");

// Check if user is already logged in
document.addEventListener("DOMContentLoaded", () => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser"));
    if (currentUser) {
        window.location.href = "index.html";
    }
});

// Form submission
registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
        name: nameInput.value.trim(),
        email: emailInput.value.trim(),
        phone: phoneInput.value.trim(),
        password: passwordInput.value.trim(),
        confirmPassword: confirmPasswordInput.value.trim(),
    };

    // Validation
    const validationError = validateForm(formData);
    if (validationError) {
        showError(validationError);
        return;
    }

    await handleRegister(formData);
});

// Form validation
function validateForm(data) {
    if (!data.name || data.name.length < 2) {
        return "يرجى إدخال اسم صحيح (حرفين على الأقل)";
    }

    if (!isValidEmail(data.email)) {
        return "يرجى إدخال بريد إلكتروني صحيح";
    }

    if (!isValidPhone(data.phone)) {
        return "يرجى إدخال رقم هاتف صحيح";
    }

    if (data.password.length < 6) {
        return "كلمة المرور يجب أن تحتوي على 6 أحرف على الأقل";
    }

    if (data.password !== data.confirmPassword) {
        return "كلمة المرور وتأكيد كلمة المرور غير متطابقتين";
    }

    return null;
}

// Handle registration
async function handleRegister(formData) {
    try {
        setLoading(true);
        hideMessages();

        const response = await fetch("/api/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            // فقط الحقول المطلوبة للـ backend
            body: JSON.stringify({
                email: formData.email,
                password: formData.password
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess("تم إنشاء الحساب بنجاح! سيتم توجيهك لصفحة تسجيل الدخول...");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 2000);
        } else {
            showError(data.error || data.message || "حدث خطأ في إنشاء الحساب");
        }
    } catch (error) {
        console.error("Registration error:", error);
        showError("حدث خطأ أثناء الاتصال بالخادم");
    } finally {
        setLoading(false);
    }
}

// Utility functions
function setLoading(loading) {
    registerBtn.disabled = loading;
    btnText.style.display = loading ? "none" : "inline";
    btnLoading.style.display = loading ? "inline" : "none";
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";
    successMessage.style.display = "none";
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = "block";
    errorMessage.style.display = "none";
}

function hideMessages() {
    errorMessage.style.display = "none";
    successMessage.style.display = "none";
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[+]?[0-9\s\-]{10,}$/;
    return phoneRegex.test(phone);
}

// Real-time validation
nameInput.addEventListener("input", function () {
    if (this.value.trim().length >= 2) {
        this.classList.remove("error");
        this.classList.add("success");
    } else {
        this.classList.remove("success");
    }
});

emailInput.addEventListener("input", function () {
    if (isValidEmail(this.value.trim())) {
        this.classList.remove("error");
        this.classList.add("success");
    } else {
        this.classList.remove("success");
    }
});

phoneInput.addEventListener("input", function () {
    if (isValidPhone(this.value.trim())) {
        this.classList.remove("error");
        this.classList.add("success");
    } else {
        this.classList.remove("success");
    }
});

passwordInput.addEventListener("input", function () {
    if (this.value.length >= 6) {
        this.classList.remove("error");
        this.classList.add("success");
    } else {
        this.classList.remove("success");
    }

    if (confirmPasswordInput.value && this.value === confirmPasswordInput.value) {
        confirmPasswordInput.classList.remove("error");
        confirmPasswordInput.classList.add("success");
    } else if (confirmPasswordInput.value) {
        confirmPasswordInput.classList.remove("success");
        confirmPasswordInput.classList.add("error");
    }
});

confirmPasswordInput.addEventListener("input", function () {
    if (this.value === passwordInput.value && this.value.length >= 6) {
        this.classList.remove("error");
        this.classList.add("success");
    } else {
        this.classList.remove("success");
        this.classList.add("error");
    }
});

[nameInput, emailInput, phoneInput, passwordInput, confirmPasswordInput].forEach((input) => {
    input.addEventListener("input", hideMessages);
});
