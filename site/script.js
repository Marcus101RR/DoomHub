// Fills in the hub status and the latest release from status.json / release.json, which the site's GitHub
// Actions job writes every 15 minutes (see .github/scripts/status.py). Nothing here contacts the hub itself.
(function () {
  function get(url) {
    return fetch(url + "?t=" + Date.now(), { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  function localTime(iso) {
    var d = new Date(iso);
    return isNaN(d) ? "" : d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  }
  get("status.json").then(function (s) {
    var box = document.getElementById("status"), text = document.getElementById("status-text");
    if (!s || !s.state) { text.textContent = "Hub status: unknown"; return; }
    box.className = "status " + s.state;
    if (s.state === "online") {
      text.textContent = "Online: " + s.players + (s.players === 1 ? " player, " : " players, ") + s.rooms + (s.rooms === 1 ? " room" : " rooms") + " · v" + s.version;
    } else if (s.state === "maintenance") {
      text.textContent = "Maintenance" + (s.reason ? ": " + s.reason : "") + " · v" + s.version;
    } else {
      text.textContent = "Offline" + (s.since ? " since " + localTime(s.since) : "");
    }
    if (s.checked) box.title = "Checked " + localTime(s.checked) + " (every 15 minutes)";
  });
  get("release.json").then(function (r) {
    if (!r || !r.version) return;
    document.getElementById("download").textContent = "Download Doom Hub v" + r.version;
    if (r.url) document.getElementById("download").href = r.url;
    var mb = r.size ? " · " + (r.size / 1048576).toFixed(1) + " MB" : "";
    document.getElementById("release").textContent = "v" + r.version + (r.date ? " · released " + new Date(r.date).toLocaleDateString() : "") + mb +
      " · Windows 10/11 · no installer · updates itself";
  });
})();
