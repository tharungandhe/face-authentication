/**
 * Small helper wrapping fetch() calls to the Face Authentication backend.
 * When the frontend is served from a different port, use the backend URL.
 */
const API_BASE = (() => {
  const origin = window.location.origin;
  if (origin === "http://127.0.0.1:8001" || origin === "http://localhost:8001") {
    return "http://127.0.0.1:8000/api";
  }
  return "/api";
})();

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || "Request failed. Please try again.");
  }
  return data;
}

/** Capture the current video frame as a base64 JPEG data-URL. */
function captureFrame(videoEl, canvasEl) {
  const width = videoEl.videoWidth;
  const height = videoEl.videoHeight;
  canvasEl.width = width;
  canvasEl.height = height;
  const ctx = canvasEl.getContext("2d");
  // Un-mirror the capture so the saved image matches natural orientation.
  ctx.translate(width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(videoEl, 0, 0, width, height);
  return canvasEl.toDataURL("image/jpeg", 0.9);
}

/**
 * Start the webcam and attach it to a <video> element. Returns the stream.
 * Throws an Error with a human-readable message on failure - callers should
 * display err.message directly rather than leaving the UI stuck on
 * "Starting camera...".
 */
async function startCamera(videoEl) {
  // getUserMedia only exists in "secure contexts": https://, or
  // http://localhost / http://127.0.0.1. If the page was opened as a
  // LAN IP (e.g. http://192.168.x.x:8000) or as a file:// path, the
  // browser won't even expose navigator.mediaDevices - this is the most
  // common reason the camera silently never starts.
  if (!window.isSecureContext) {
    throw new Error(
      "Camera blocked: this page must be opened over https://, or http://localhost. " +
      "You're on " + window.location.origin + " - try http://localhost:8000 instead."
    );
  }
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    throw new Error(
      "This browser does not expose a camera API (navigator.mediaDevices is unavailable)."
    );
  }

  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 400 }, facingMode: "user" },
      audio: false,
    });
  } catch (err) {
    // Translate the raw DOMException into something actionable.
    const messages = {
      NotAllowedError: "Camera permission was denied. Click the camera/lock icon in the address bar and allow access, then reload.",
      NotFoundError: "No camera was found on this device.",
      NotReadableError: "The camera is already in use by another app or browser tab. Close it and try again.",
      OverconstrainedError: "No camera matches the requested resolution. Try a different device.",
      SecurityError: "Camera access is blocked by the browser's security settings for this page.",
      AbortError: "Camera start-up was interrupted. Please try again.",
    };
    throw new Error(messages[err.name] || `Could not start the camera (${err.name || err.message}).`);
  }

  videoEl.srcObject = stream;

  // Wait for the video to actually have a frame ready, not just for
  // play() to resolve - on some browsers play() resolves before the
  // stream has real dimensions, which made capture silently fail.
  await new Promise((resolve, reject) => {
    const onReady = () => {
      videoEl.removeEventListener("loadedmetadata", onReady);
      resolve();
    };
    videoEl.addEventListener("loadedmetadata", onReady);
    videoEl.play().catch(reject);
    // Safety net in case loadedmetadata already fired before the listener attached.
    if (videoEl.readyState >= 2) resolve();
  });

  return stream;
}
