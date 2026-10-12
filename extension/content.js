/**
 * Gemini Quota & Usage Bridge - Content Script (v1.1)
 * Robust dual-strategy scraper: Hidden Iframe + Active DOM + Turkish & English parser
 */

(function () {
    const BRIDGE_API_URL = "http://127.0.0.1:38281/api/usage";
    let isScraping = false;
    let lastSyncedHash = "";
    let iframeEl = null;

    console.log("[Gemini Quota Bridge] Content script v1.1 initialized on gemini.google.com");

    /**
     * Send parsed usage data to local desktop top bar
     */
    async function sendUsageToTopBar(data) {
        try {
            const resp = await fetch(BRIDGE_API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (resp.ok) {
                console.log("[Gemini Quota Bridge] ✅ Sent to Windows Top Bar:", data);
            }
        } catch (err) {
            console.warn("[Gemini Quota Bridge] Top Bar offline or unreachable:", err.message);
        }
    }

    /**
     * Parse seconds from strings like "3 hr 15 min", "3 saat 25 dakika", "2s 40d", "03:15:00"
     */
    function parseResetSeconds(text) {
        if (!text) return 0;
        let total = 0;
        const lower = text.toLowerCase();

        // Hours: 3 hr, 3 saat, 3h, 3 hours
        const hMatch = lower.match(/(\d+)\s*(?:h|hr|hours?|saat)/);
        if (hMatch) total += parseInt(hMatch[1], 10) * 3600;

        // Minutes: 25 min, 25 dakika, 25m, 25 dk
        const mMatch = lower.match(/(\d+)\s*(?:m|min|mins|minutes?|dakika|dk)/);
        if (mMatch) total += parseInt(mMatch[1], 10) * 60;

        // Seconds: 30 sec, 30 saniye, 30s
        const sMatch = lower.match(/(\d+)\s*(?:s|sec|secs|seconds?|saniye)/);
        if (sMatch) total += parseInt(sMatch[1], 10);

        // Colon format "03:45"
        if (total === 0) {
            const colonMatch = lower.match(/(\d{1,2}):(\d{2})/);
            if (colonMatch) {
                total = parseInt(colonMatch[1], 10) * 3600 + parseInt(colonMatch[2], 10) * 60;
            }
        }
        return total;
    }

    /**
     * Extract percentage from text chunk (handles Turkish %88 and English 88%, 'kalan' & 'kullanılan')
     */
    function extractPercentFromChunk(chunk) {
        if (!chunk) return null;
        const lower = chunk.toLowerCase();

        // Check if explicitly 'used' or 'kullanılan' -> Remaining = 100 - val
        const usedMatch = lower.match(/(?:kullanılan|used|tüketilen)\s*:?\s*%?\s*(\d{1,3})|%?\s*(\d{1,3})\s*%?\s*(?:kullanılan|used|tüketilen)/i);
        if (usedMatch) {
            const val = parseInt(usedMatch[1] || usedMatch[2], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return 100 - val;
        }

        // Check for 'kalan' or 'remaining'
        const remainingMatch = lower.match(/(?:kalan|remaining)\s*:?\s*%?\s*(\d{1,3})|%?\s*(\d{1,3})\s*%?\s*(?:kalan|remaining)/i);
        if (remainingMatch) {
            const val = parseInt(remainingMatch[1] || remainingMatch[2], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return val;
        }

        // Turkish format: %88 or % 88
        const trMatch = chunk.match(/%\s*(\d{1,3})/);
        if (trMatch) {
            const val = parseInt(trMatch[1], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return val;
        }

        // English format: 88% or 88 %
        const enMatch = chunk.match(/(\d{1,3})\s*%/);
        if (enMatch) {
            const val = parseInt(enMatch[1], 10);
            if (!isNaN(val) && val >= 0 && val <= 100) return val;
        }

        return null;
    }

    /**
     * Parse HTML / Document node containing usage metrics
     */
    function parseUsageFromDocument(docOrElement) {
        if (!docOrElement) return null;
        const text = docOrElement.innerText || docOrElement.textContent || "";
        if (!text || text.length < 5) return null;

        let remaining = null;
        let resetSeconds = 0;
        let resetTimeStr = "";
        let weeklyRemaining = null;
        let plan = "Google AI Pro";

        // 1. Check progress bars in DOM: aria-valuenow
        const progressBars = docOrElement.querySelectorAll ? docOrElement.querySelectorAll('[role="progressbar"], mat-progress-bar, .progress-bar') : [];
        for (const pb of progressBars) {
            const val = pb.getAttribute('aria-valuenow');
            if (val !== null && !isNaN(val)) {
                const num = parseFloat(val);
                if (num >= 0 && num <= 100) {
                    const label = (pb.getAttribute('aria-label') || '').toLowerCase();
                    if (label.includes('used') || label.includes('kullanılan')) {
                        remaining = 100 - num;
                    } else {
                        remaining = num;
                    }
                    console.log("[Gemini Quota Bridge] Found progressbar value:", remaining);
                    break;
                }
            }
        }

        // 2. Scan text lines specifically looking for 5-hour limit / 5 saatlik limit
        const lines = text.split(/\r?\n/);
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lower = line.toLowerCase();
            if (lower.includes('5-hour') || lower.includes('5 saat') || lower.includes('5h') || lower.includes('beş saat') || lower.includes('kullanım')) {
                const chunk = lines.slice(Math.max(0, i - 1), i + 4).join(' ');
                const pct = extractPercentFromChunk(chunk);
                if (pct !== null) {
                    remaining = pct;
                    console.log("[Gemini Quota Bridge] Matched 5-hour percentage from text chunk:", remaining, "Chunk:", chunk);
                    break;
                }
            }
        }

        // 3. Fallback: Scan full text for any percentage
        if (remaining === null) {
            remaining = extractPercentFromChunk(text);
        }

        // 4. Extract reset countdown string
        const resetMatch = text.match(/(?:refreshes? in|resets? in|yenilenme süresi|kalan süre|yenilenir)[^\n\r\.\,\<]{1,50}/i);
        if (resetMatch) {
            resetTimeStr = resetMatch[0].trim();
            resetSeconds = parseResetSeconds(resetTimeStr);
            console.log("[Gemini Quota Bridge] Found reset time string:", resetTimeStr, "Parsed seconds:", resetSeconds);
        }

        // 5. Plan detection
        if (/ultra/i.test(text)) plan = "Google AI Ultra";
        else if (/plus/i.test(text)) plan = "Google AI Plus";
        else if (/pro/i.test(text)) plan = "Google AI Pro";

        if (remaining !== null) {
            return {
                remaining: remaining,
                reset_seconds: resetSeconds > 0 ? resetSeconds : 18000,
                reset_time_str: resetTimeStr,
                weekly_remaining: weeklyRemaining,
                plan: plan,
                source: window.location.pathname.includes('/usage') ? "gemini.google.com/usage" : "gemini.google.com (iframe)",
                timestamp: Date.now()
            };
        }
        return null;
    }

    /**
     * Check if active page itself is /usage or if modal is open
     */
    function scanActivePageDOM() {
        // A. Are we directly on /usage?
        if (window.location.pathname.includes('/usage')) {
            console.log("[Gemini Quota Bridge] Scanning active /usage page...");
            const data = parseUsageFromDocument(document.body);
            if (data) {
                sendUsageToTopBar(data);
                return true;
            }
        }

        // B. Is there an open modal / dialog?
        const dialogs = document.querySelectorAll('div[role="dialog"], mat-dialog-container, .cdk-overlay-pane');
        for (const dlg of dialogs) {
            const text = dlg.innerText || "";
            if (text.includes("limit") || text.includes("kullanım") || text.includes("usage") || text.includes("5-hour") || text.includes("5 saat")) {
                console.log("[Gemini Quota Bridge] Scanning open modal dialog...");
                const data = parseUsageFromDocument(dlg);
                if (data) {
                    sendUsageToTopBar(data);
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Strategy 2: Load hidden same-origin iframe to https://gemini.google.com/usage
     */
    function triggerIframeScrape() {
        if (isScraping) return;
        isScraping = true;

        if (!iframeEl) {
            iframeEl = document.createElement("iframe");
            iframeEl.id = "gemini-usage-bridge-iframe";
            iframeEl.style.cssText = "position:fixed;top:-9999px;left:-9999px;width:300px;height:300px;opacity:0;pointer-events:none;z-index:-1;";
            document.body.appendChild(iframeEl);
        }

        // Add cache-busting timestamp
        iframeEl.src = "https://gemini.google.com/usage?t=" + Date.now();
        console.log("[Gemini Quota Bridge] Loading background iframe to fetch live quota...");

        // Wait for iframe Angular app to render
        let checkCount = 0;
        const intervalId = setInterval(() => {
            checkCount++;
            try {
                const iDoc = iframeEl.contentDocument || (iframeEl.contentWindow && iframeEl.contentWindow.document);
                if (iDoc && iDoc.body) {
                    const data = parseUsageFromDocument(iDoc.body);
                    if (data && data.remaining !== null) {
                        clearInterval(intervalId);
                        isScraping = false;
                        const hash = `${data.remaining}_${data.reset_seconds}`;
                        if (hash !== lastSyncedHash) {
                            lastSyncedHash = hash;
                            sendUsageToTopBar(data);
                        }
                        return;
                    }
                }
            } catch (err) {
                // Cross-origin or frame block
            }

            if (checkCount >= 10) { // Timeout after 10 * 600ms = 6s
                clearInterval(intervalId);
                isScraping = false;
            }
        }, 600);
    }

    /**
     * Master refresh trigger
     */
    function triggerFullSync() {
        // 1. Try scanning current page first
        const foundOnPage = scanActivePageDOM();
        if (!foundOnPage) {
            // 2. Trigger background iframe
            triggerIframeScrape();
        }
    }

    /**
     * Watch for chat responses and DOM changes
     */
    function observeChat() {
        const observer = new MutationObserver(() => {
            // Check modal whenever DOM changes
            scanActivePageDOM();

            // Check if stop generation button disappears (response completed)
            const stopBtn = document.querySelector('button[aria-label*="Stop"], button[aria-label*="Durdur"]');
            if (!stopBtn && window._hadStopBtn) {
                window._hadStopBtn = false;
                console.log("[Gemini Quota Bridge] Response generation complete! Refreshing quota in 1.5s...");
                setTimeout(triggerFullSync, 1500);
            } else if (stopBtn) {
                window._hadStopBtn = true;
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Listen for manual sync requests from extension popup
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
        chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
            if (msg && msg.action === "force_sync") {
                console.log("[Gemini Quota Bridge] Received force_sync request from popup");
                triggerFullSync();
                sendResponse({ status: "syncing" });
            }
        });
    }

    // Initial triggers
    setTimeout(triggerFullSync, 1500);
    setInterval(triggerFullSync, 60000); // Poll every 60s

    if (document.body) {
        observeChat();
    } else {
        window.addEventListener("DOMContentLoaded", observeChat);
    }
})();
