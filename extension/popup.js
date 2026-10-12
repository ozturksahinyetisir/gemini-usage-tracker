const BRIDGE_STATUS_URL = "http://127.0.0.1:38281/api/status";
const BRIDGE_USAGE_URL = "http://127.0.0.1:38281/api/usage";

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
            if (!document.getElementById("quick-pct").value) {
                document.getElementById("quick-pct").value = Math.round(data.remaining);
            }
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
    const msg = document.getElementById("msg");
    msg.textContent = "Taranıyor...";
    msg.style.color = "#8AB4F8";

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].url && tabs[0].url.includes("gemini.google.com")) {
            chrome.tabs.sendMessage(tabs[0].id, { action: "force_sync" }, (response) => {
                setTimeout(() => {
                    checkStatus();
                    msg.textContent = "✅ Eşitleme tamamlandı!";
                    msg.style.color = "#81C995";
                }, 1500);
            });
        } else {
            // Check status directly
            setTimeout(() => {
                checkStatus();
                msg.textContent = "Aktif sekme Gemini değil!";
                msg.style.color = "#F28B82";
            }, 500);
        }
    });
});

document.getElementById("set-btn").addEventListener("click", async () => {
    const val = parseFloat(document.getElementById("quick-pct").value);
    const msg = document.getElementById("msg");
    if (isNaN(val) || val < 0 || val > 100) {
        msg.textContent = "Lütfen 0-100 arası bir sayı girin!";
        msg.style.color = "#F28B82";
        return;
    }

    try {
        const resp = await fetch(BRIDGE_USAGE_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                remaining: val,
                reset_seconds: 18000,
                source: "Eklenti Popup Hızlı Giriş"
            })
        });
        if (resp.ok) {
            msg.textContent = "✅ %" + val + " olarak güncellendi!";
            msg.style.color = "#81C995";
            checkStatus();
        }
    } catch (e) {
        msg.textContent = "Masaüstü uygulamasına ulaşılamadı!";
        msg.style.color = "#F28B82";
    }
});

checkStatus();
