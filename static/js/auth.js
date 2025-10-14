document.addEventListener("DOMContentLoaded", () => {
  // Tab switching functionality
  const tabBtns = document.querySelectorAll(".tab-btn");
  const formContents = document.querySelectorAll(".form-content");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;

      // Update active states
      tabBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      formContents.forEach((content) => {
        content.classList.remove("active");
      });

      if (tab === "login") {
        document.getElementById("loginContent").classList.add("active");
      } else {
        document.getElementById("registerContent").classList.add("active");
      }

      // Clear any error messages
      document.querySelectorAll(".message").forEach((msg) => {
        msg.style.display = "none";
        msg.textContent = "";
      });
    });
  });

  // Login form submission
  const loginForm = document.getElementById("loginForm");
  const loginError = document.getElementById("loginError");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    // Clear previous errors
    loginError.style.display = "none";
    loginError.textContent = "";

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (data.success) {
        // Redirect to home page
        window.location.href = "/home";
      } else {
        loginError.textContent = data.message;
        loginError.style.display = "block";
      }
    } catch (error) {
      loginError.textContent = "An error occurred. Please try again.";
      loginError.style.display = "block";
    }
  });

  // Register form submission
  const registerForm = document.getElementById("registerForm");
  const registerError = document.getElementById("registerError");

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("registerName").value;
    const username = document.getElementById("registerUsername").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    const confirmPassword = document.getElementById(
      "registerConfirmPassword"
    ).value;

    // Clear previous errors
    registerError.style.display = "none";
    registerError.textContent = "";

    // Client-side validation
    if (!name || !username || !email || !password || !confirmPassword) {
      registerError.textContent = "All fields are required";
      registerError.style.display = "block";
      return;
    }

    if (password !== confirmPassword) {
      registerError.textContent = "Passwords do not match";
      registerError.style.display = "block";
      return;
    }

    if (password.length < 6) {
      registerError.textContent = "Password must be at least 6 characters";
      registerError.style.display = "block";
      return;
    }

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          username,
          email,
          password,
          confirmPassword,
        }),
      });

      const data = await response.json();

      if (data.success) {
        // Redirect to home page
        window.location.href = "/home";
      } else {
        registerError.textContent = data.message;
        registerError.style.display = "block";
      }
    } catch (error) {
      registerError.textContent = "An error occurred. Please try again.";
      registerError.style.display = "block";
    }
  });
});
