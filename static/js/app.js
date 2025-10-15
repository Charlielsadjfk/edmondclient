// Service Worker Registration
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("/static/js/serviceworker.js")
      .then((res) => console.log("Service worker registered successfully"))
      .catch((err) => console.log("Service worker registration failed", err));
  });
}

// PWA Install Prompt
let deferredPrompt;

window.addEventListener("beforeinstallprompt", (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  console.log("PWA install prompt available");
});

window.addEventListener("appinstalled", () => {
  console.log("PWA was installed");
  deferredPrompt = null;
});
