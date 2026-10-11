/**
 * Gemini Quota & Usage Bridge - Content Script
 * Runs on gemini.google.com and syncs live 5-hour quota and countdown with the Windows Top Bar.
 */

(function () {
    const BRIDGE_API_URL = "http://127.0.0.1:38281/api/usage";
    const LOG_PROMPT_URL = "http://127.0.0.1:38281/api/log_prompt";
    let isFetchingUsage = false;
    let lastSyncedHash = "";

    console.log("[Gemini Quota Bridge] Content script initialized on gemini.google.com");

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
                console.log("[Gemini Quota Bridge] Successfully synced with Windows Top Bar:", data);
            }
        } catch (err) {
            // Local app might be closed or starting
            // console.warn("[Gemini Quota Bridge] Top Bar offline or unreachable:", err.message);
        }
    }

    /**
     * Parse seconds from string like "3 hr 15 min", "2s 40d", "03:15:00"
     */
    function parseResetSeconds(text) {
        if (!text) return 0;
        let total = 0;
        const lower = text.toLowerCase();

        // Hours
        const hMatch = lower.match(/(\d+)\s*(?:h|hr|hours?|saat)/);
        if (hMatch) total += parseInt(hMatch[1], 10) * 3600;

        // Minutes
        const mMatch = lower.match(/(\d+)\s*(?:m|min|mins|minutes?|dakika|dk)/);
        if (mMatch) total += parseInt(mMatch[1], 10) * 60;

        // Seconds
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
     * Extract usage from https://gemini.google.com/usage
     */
    async function fetchUsageFromOfficialPage() {
        if (isFetchingUsage) return;
        isFetchingUsage = true;
        try {
            const res = await fetch("https://gemini.google.com/usage", {
                credentials: "include"
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const htmlText = await res.text();
            parseAndSyncHtml(htmlText);
        } catch (err) {
            console.log("[Gemini Quota Bridge] fetch usage page note:", err.message);
        } finally {
            isFetchingUsage = false;
        }
    }

    /**
     * Parse HTML or DOM containing usage stats
     */
    function parseAndSyncHtml(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const bodyText = doc.body ? doc.body.innerText : html;

        let remaining = null;
        let resetSeconds = 0;
        let weeklyRemaining = null;
        let plan = "Google AI Pro";

        // Try extracting percentages
        // Common phrases: "Remaining: 85%", "Kalan: %85", "85% remaining"
        const percentMatches = [...bodyText.matchAll(/(\d{1,3})\s*%/g)];
        if (percentMatches.length > 0) {
            // Usually the primary percentage is the first or largest relevant number
            for (const m of percentMatches) {
                const val = parseInt(m[1], 10);
                if (val >= 0 && val <= 100) {
                    remaining = val;
                    break;
                }
            }
        }

        // Try extracting reset time
        // Matches "Refreshes in X hr Y min" or "Yenilenme süresi: X saat"
        const resetMatch = bodyText.match(/(?:refreshes? in|resets? in|yenilenme süresi|kalan süre)[^\n\r\.\,\<]{1,40}/i);
        if (resetMatch) {
            resetSeconds = parseResetSeconds(resetMatch[0]);
        }

        // Check for plan tier keywords
        if (bodyText.includes("Ultra")) plan = "Google AI Ultra";
        else if (bodyText.includes("Plus")) plan = "Google AI Plus";
        else if (bodyText.includes("Pro")) plan = "Google AI Pro";

        if (remaining !== null || resetSeconds > 0) {
            const payload = {
                remaining: remaining !== null ? remaining : 100,
                reset_seconds: resetSeconds > 0 ? resetSeconds : 18000,
                reset_time_str: resetMatch ? resetMatch[0] : "",
                weekly_remaining: weeklyRemaining,
                plan: plan,
                source: "gemini.google.com",
                timestamp: Date.now()
            };

            const hash = `${payload.remaining}_${payload.reset_seconds}`;
            if (hash !== lastSyncedHash) {
                lastSyncedHash = hash;
                sendUsageToTopBar(payload);
            }
        }
    }

    /**
     * Inspect active modal if user opened "Settings > Usage Limits" directly in UI
     */
    function inspectActiveModal() {
        const dialogs = document.querySelectorAll('div[role="dialog"], mat-dialog-container, .cdk-overlay-pane');
        for (const dlg of dialogs) {
            const text = dlg.innerText || "";
            if (text.includes("Usage limits") || text.includes("Kullanım limitleri") || text.includes("5-hour") || text.includes("5 saatlik")) {
                parseAndSyncHtml(text);
                break;
            }
        }
    }

    /**
     * Watch for chat submissions and response completions
     */
    function observeChatActivity() {
        const observer = new MutationObserver(() => {
            // Check for modal dialogs
            inspectActiveModal();

            // Check if stop generation button appears/disappears
            const stopBtn = document.querySelector('button[aria-label*="Stop"], button[aria-label*="Durdur"]');
            if (!stopBtn && window._lastHadStopBtn) {
                // Generation just finished! Wait 1.5s then fetch usage
                window._lastHadStopBtn = false;
                setTimeout(fetchUsageFromOfficialPage, 1800);
            } else if (stopBtn) {
                window._lastHadStopBtn = true;
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Initial check and periodic polling (every 90 seconds while tab is active)
    setTimeout(fetchUsageFromOfficialPage, 2000);
    setInterval(fetchUsageFromOfficialPage, 90000);

    // Start observer
    if (document.body) {
        observeChatActivity();
    } else {
        window.addEventListener("DOMContentLoaded", observeChatActivity);
    }
})();
