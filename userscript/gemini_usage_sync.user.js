// ==UserScript==
// @name         Gemini Usage & Quota Bridge for Windows Top Bar
// @namespace    https://github.com/google/gemini
// @version      1.1.0
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
    let lastSyncedHash = "";
    let isScraping = false;

    console.log("[Gemini Usage Userscript v1.1] Initialized on gemini.google.com");

    function sendToTopBar(data) {
        if (typeof GM_xmlhttpRequest !== "undefined") {
            GM_xmlhttpRequest({
                method: "POST",
                url: BRIDGE_API_URL,
                headers: { "Content-Type": "application/json" },
                data: JSON.stringify(data),
                onload: function(response) {
                    console.log("[Gemini Usage Userscript] Synced with Top Bar:", data);
                }
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
        if (total === 0) {
            const colonMatch = lower.match(/(\d{1,2}):(\d{2})/);
            if (colonMatch) {
                total = parseInt(colonMatch[1], 10) * 3600 + parseInt(colonMatch[2], 10) * 60;
            }
        }
        return total;
    }

    function extractPercentFromChunk(chunk) {
        if (!chunk) return null;
        const lower = chunk.toLowerCase();
        const usedMatch = lower.match(/(?:kullanılan|used|tüketilen)\s*:?\s*%?\s*(\d{1,3})|%?\s*(\d{1,3})\s*%?\s*(?:kullanılan|used|tüketilen)/i);
        if (usedMatch) {
            const val = parseInt(usedMatch[1] || usedMatch[2], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return 100 - val;
        }
        const remainingMatch = lower.match(/(?:kalan|remaining)\s*:?\s*%?\s*(\d{1,3})|%?\s*(\d{1,3})\s*%?\s*(?:kalan|remaining)/i);
        if (remainingMatch) {
            const val = parseInt(remainingMatch[1] || remainingMatch[2], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return val;
        }
        const trMatch = chunk.match(/%\s*(\d{1,3})/);
        if (trMatch) {
            const val = parseInt(trMatch[1], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return val;
        }
        const enMatch = chunk.match(/(\d{1,3})\s*%/);
        if (enMatch) {
            const val = parseInt(enMatch[1], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return val;
        }
        return null;
    }

    function scanNode(node) {
        if (!node) return null;
        const text = node.innerText || node.textContent || "";
        if (!text || text.length < 5) return null;

        let remaining = null;
        let resetSeconds = 0;
        let resetTimeStr = "";

        const pbs = node.querySelectorAll ? node.querySelectorAll('[role="progressbar"], mat-progress-bar, .progress-bar') : [];
        for (const pb of pbs) {
            const val = pb.getAttribute('aria-valuenow');
            if (val !== null && !isNaN(val)) {
                const num = parseFloat(val);
                if (num >= 0 && num <= 100) {
                    const label = (pb.getAttribute('aria-label') || '').toLowerCase();
                    remaining = (label.includes('used') || label.includes('kullanılan')) ? (100 - num) : num;
                    break;
                }
            }
        }

        const lines = text.split(/\r?\n/);
        for (let i = 0; i < lines.length; i++) {
            const lower = lines[i].toLowerCase();
            if (lower.includes('5-hour') || lower.includes('5 saat') || lower.includes('5h') || lower.includes('kullanım')) {
                const chunk = lines.slice(Math.max(0, i - 1), i + 4).join(' ');
                const pct = extractPercentFromChunk(chunk);
                if (pct !== null) {
                    remaining = pct;
                    break;
                }
            }
        }

        if (remaining === null) {
            remaining = extractPercentFromChunk(text);
        }

        const resetMatch = text.match(/(?:refreshes? in|resets? in|yenilenme süresi|kalan süre|yenilenir)[^\n\r\.\,\<]{1,50}/i);
        if (resetMatch) {
            resetTimeStr = resetMatch[0].trim();
            resetSeconds = parseResetSeconds(resetTimeStr);
        }

        if (remaining !== null) {
            return {
                remaining: remaining,
                reset_seconds: resetSeconds > 0 ? resetSeconds : 18000,
                reset_time_str: resetTimeStr,
                source: "Userscript",
                timestamp: Date.now()
            };
        }
        return null;
    }

    function checkActiveDOM() {
        if (window.location.pathname.includes('/usage')) {
            const data = scanNode(document.body);
            if (data) {
                sendToTopBar(data);
                return true;
            }
        }
        const dialogs = document.querySelectorAll('div[role="dialog"], mat-dialog-container, .cdk-overlay-pane');
        for (const dlg of dialogs) {
            const data = scanNode(dlg);
            if (data) {
                sendToTopBar(data);
                return true;
            }
        }
        return false;
    }

    function triggerIframeScrape() {
        if (isScraping) return;
        isScraping = true;
        let iframe = document.getElementById("gemini-usage-userscript-iframe");
        if (!iframe) {
            iframe = document.createElement("iframe");
            iframe.id = "gemini-usage-userscript-iframe";
            iframe.style.cssText = "position:fixed;top:-9999px;left:-9999px;width:300px;height:300px;opacity:0;pointer-events:none;z-index:-1;";
            document.body.appendChild(iframe);
        }
        iframe.src = "https://gemini.google.com/usage?t=" + Date.now();
        let count = 0;
        const interval = setInterval(() => {
            count++;
            try {
                const iDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (iDoc && iDoc.body) {
                    const data = scanNode(iDoc.body);
                    if (data && data.remaining !== null) {
                        clearInterval(interval);
                        isScraping = false;
                        const hash = `${data.remaining}_${data.reset_seconds}`;
                        if (hash !== lastSyncedHash) {
                            lastSyncedHash = hash;
                            sendToTopBar(data);
                        }
                        return;
                    }
                }
            } catch(e) {}
            if (count >= 10) {
                clearInterval(interval);
                isScraping = false;
            }
        }, 600);
    }

    function sync() {
        if (!checkActiveDOM()) {
            triggerIframeScrape();
        }
    }

    setTimeout(sync, 2000);
    setInterval(sync, 60000);
    const observer = new MutationObserver(() => checkActiveDOM());
    if (document.body) observer.observe(document.body, { childList: true, subtree: true });
})();
