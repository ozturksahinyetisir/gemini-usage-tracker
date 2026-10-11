const BRIDGE_STATUS_URL = "http://127.0.0.1:38281/api/status";

async function checkStatus() {
    const dot = document.getElementById("dot");
    const statusText = document.getElementById("status-text");
    const quotaVal = document.getElementById("quota-val");
    const timerVal = document.getElementById("timer-val");
    const planVal = document.getElementById("plan-val");

    try {
        const res = await fetch(BRIDGE_STATUS_URL);
        if (res.ok) {
            const data = await res.json();
            dot.className = "status-dot";
            statusText.textContent = "Bağlı";
            statusText.style.color = "#81C995";
            quotaVal.textContent = `%${data.remaining.toFixed(0)} Kalan`;
            timerVal.textContent = data.countdown_str || "00:00:00";
            planVal.textContent = data.plan || "Google AI Pro";
        } else {
            throw new Error();
        }
    } catch (e) {
        dot.className = "status-dot offline";
        statusText.textContent = "Çevrimdışı";
        statusText.style.color = "#EA4335";
    }
}

document.getElementById("sync-btn").addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].url.includes("gemini.google.com")) {
            chrome.scripting.executeScript({
                target: { tabId: tabs[0].id },
                func: () => {
                    window.location.reload();
                }
            });
        }
        checkStatus();
    });
});

checkStatus();
