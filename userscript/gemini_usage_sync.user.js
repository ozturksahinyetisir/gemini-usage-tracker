// ==UserScript==
// @name         Gemini Usage & Quota Bridge for Windows Top Bar
// @namespace    https://github.com/google/gemini
// @version      1.0.0
// @description  Automatically syncs Gemini 5-hour rolling usage limit & reset countdown with your Windows Top Menu Bar
// @author       Gemini Usage Tracker
// @match        https://gemini.google.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    const BRIDGE_API_URL = "http://127.0.0.1:38281/api/usage";
    let isFetchingUsage = false;
    let lastSyncedHash = "";

    console.log("[Gemini Usage Userscript] Initialized on gemini.google.com");

    function sendToTopBar(data) {
        if (typeof GM_xmlhttpRequest !== "undefined") {
            GM_xmlhttpRequest({
                method: "POST",
                url: BRIDGE_API_URL,
                headers: { "Content-Type": "application/json" },
                data: JSON.stringify(data),
                onload: function(response) {
                    console.log("[Gemini Usage Userscript] Synced with Top Bar:", data);
                },
                onerror: function(err) {}
            });
        } else {
            fetch(BRIDGE_API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            }).catch(() => {});
        }
    }

    function parseResetSeconds(text) {
        if (!text) return 0;
        let total = 0;
        const lower = text.toLowerCase();
        const hMatch = lower.match(/(\d+)\s*(?:h|hr|hours?|saat)/);
        if (hMatch) total += parseInt(hMatch[1], 10) * 3600;
        const mMatch = lower.match(/(\d+)\s*(?:m|min|mins|minutes?|dakika|dk)/);
        if (mMatch) total += parseInt(mMatch[1], 10) * 60;
        const sMatch = lower.match(/(\d+)\s*(?:s|sec|secs|seconds?|saniye)/);
        if (sMatch) total += parseInt(sMatch[1], 10);
        return total;
    }

    async function checkUsage() {
        if (isFetchingUsage) return;
        isFetchingUsage = true;
        try {
            const res = await fetch("https://gemini.google.com/usage", { credentials: "include" });
            if (!res.ok) return;
            const text = await res.text();
            
            let remaining = null;
            let resetSeconds = 0;
            const percentMatches = [...text.matchAll(/(\d{1,3})\s*%/g)];
            if (percentMatches.length > 0) {
                remaining = parseInt(percentMatches[0][1], 10);
            }

            const resetMatch = text.match(/(?:refreshes? in|resets? in|yenilenme süresi|kalan süre)[^\n\r\.\,\<]{1,40}/i);
            if (resetMatch) {
                resetSeconds = parseResetSeconds(resetMatch[0]);
            }

            if (remaining !== null || resetSeconds > 0) {
                const payload = {
                    remaining: remaining !== null ? remaining : 100,
                    reset_seconds: resetSeconds > 0 ? resetSeconds : 18000,
                    reset_time_str: resetMatch ? resetMatch[0] : "",
                    source: "Tampermonkey Userscript",
                    timestamp: Date.now()
                };
                const hash = `${payload.remaining}_${payload.reset_seconds}`;
                if (hash !== lastSyncedHash) {
                    lastSyncedHash = hash;
                    sendToTopBar(payload);
                }
            }
        } catch(e) {
        } finally {
            isFetchingUsage = false;
        }
    }

    setTimeout(checkUsage, 2000);
    setInterval(checkUsage, 90000);
})();
