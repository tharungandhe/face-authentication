(function () {
  const video = document.getElementById("register-video");
  const canvas = document.getElementById("register-canvas");
  const placeholder = document.getElementById("register-placeholder");
  const usernameInput = document.getElementById("reg-username");
  const fullNameInput = document.getElementById("reg-fullname");
  const registerBtn = document.getElementById("register-btn");
  const resultBox = document.getElementById("register-result");

  if (!video) return; // this page doesn't have a registration panel

  async function init() {
    try {
      await startCamera(video);
      placeholder.classList.add("hidden");
    } catch (err) {
      console.error("Camera error:", err);
      placeholder.querySelector("span").textContent = err.message;
    }
  }

  function showResult(success, message) {
    resultBox.classList.remove("hidden", "success", "error");
    resultBox.classList.add(success ? "success" : "error");
    resultBox.textContent = message;
  }

  registerBtn.addEventListener("click", async () => {
    const username = usernameInput.value.trim();
    const fullName = fullNameInput.value.trim();

    if (!username || !fullName) {
      showResult(false, "Please enter both a username and your full name.");
      return;
    }
    if (video.readyState < 2) {
      showResult(false, "Camera is not ready yet. Please wait a moment.");
      return;
    }

    registerBtn.disabled = true;
    registerBtn.textContent = "Registering…";

    try {
      const frame = captureFrame(video, canvas);
      const data = await apiPost("/register", {
        username,
        full_name: fullName,
        image: frame,
      });
      showResult(true, `${data.message} Redirecting to login...`);
      usernameInput.value = "";
      fullNameInput.value = "";

      setTimeout(() => {
        const params = new URLSearchParams({
          fromRegister: "1",
          username,
        });
        window.location.href = `login.html?${params.toString()}`;
      }, 1600);
    } catch (err) {
      showResult(false, err.message);
      registerBtn.disabled = false;
      registerBtn.innerHTML =
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 8h3l2-3h6l2 3h3v11H4V8z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="13" r="3.2" stroke="currentColor" stroke-width="1.8"/></svg> Capture &amp; Register';
    }
  });

  init();
})();
