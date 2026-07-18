(function () {
  const video = document.getElementById("login-video");
  const canvas = document.getElementById("login-canvas");
  const placeholder = document.getElementById("login-placeholder");
  const statusRow = document.getElementById("login-status");
  const statusText = document.getElementById("login-status-text");
  const authBtn = document.getElementById("authenticate-btn");
  const resultBox = document.getElementById("login-result");

  if (!video) return; // this page doesn't have a login panel

  const urlParams = new URLSearchParams(window.location.search);
  const fromRegister = urlParams.get("fromRegister") === "1";
  const registeredUsername = urlParams.get("username");
  let faceCheckInterval = null;
  let faceCurrentlyDetected = false;
  let autoAuthPending = fromRegister;

  function setStatus(detected, message) {
    faceCurrentlyDetected = detected;
    statusRow.classList.toggle("detected", detected);
    statusText.textContent = message;
    authBtn.disabled = !detected;
    if (detected && autoAuthPending) {
      autoAuthPending = false;
      authenticateFace();
    }
  }

  async function pollFaceCheck() {
    if (video.readyState < 2) return;
    try {
      const frame = captureFrame(video, canvas);
      const data = await apiPost("/face-check", { image: frame });
      if (data.face_detected) {
        setStatus(true, "Face detected. Ready to authenticate.");
      } else {
        setStatus(false, "No face detected. Please align your face in the frame.");
      }
    } catch (err) {
      setStatus(false, "Unable to reach the server.");
    }
  }

  async function authenticateFace() {
    if (!faceCurrentlyDetected) return;
    authBtn.disabled = true;
    authBtn.textContent = "Authenticating…";

    try {
      const frame = captureFrame(video, canvas);
      const data = await apiPost("/authenticate", { image: frame });

      if (data.success) {
        showResult(true, `Welcome back, ${data.full_name}! (confidence: ${data.confidence}%)`);
      } else {
        const conf = data.confidence != null ? ` (confidence: ${data.confidence}%)` : "";
        showResult(false, `${data.message}${conf}`);
      }
    } catch (err) {
      showResult(false, err.message);
    } finally {
      authBtn.innerHTML =
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6" stroke="currentColor" stroke-width="1.8"/></svg> Authenticate';
      authBtn.disabled = !faceCurrentlyDetected;
    }
  }

  async function init() {
    try {
      await startCamera(video);
      placeholder.classList.add("hidden");
      statusText.textContent = fromRegister
        ? `Registration complete. Align your face to verify login for ${registeredUsername || 'your account'}...`
        : "Looking for your face…";
      faceCheckInterval = setInterval(pollFaceCheck, 1200);
    } catch (err) {
      console.error("Camera error:", err);
      placeholder.querySelector("span").textContent = err.message;
      statusText.textContent = "Camera unavailable.";
    }
  }

  function showResult(success, message) {
    resultBox.classList.remove("hidden", "success", "error");
    resultBox.classList.add(success ? "success" : "error");
    resultBox.textContent = message;
  }

  authBtn.addEventListener("click", async () => {
    if (!faceCurrentlyDetected) return;
    await authenticateFace();
  });

  init();
})();
