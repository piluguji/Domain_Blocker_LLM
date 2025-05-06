async function loadInitialRules() {
  try {
    const response = await fetch("http://127.0.0.1:5000/get_rules");
    const rules = await response.json();

    await chrome.declarativeNetRequest.updateDynamicRules({
      removeRuleIds: (await chrome.declarativeNetRequest.getDynamicRules()).map(r => r.id),
      addRules: rules
    });

    console.log("Fetched and loaded rules from server.");
  } catch (error) {
    console.error("Failed to load rules from server:", error);
  }
}

async function classifyAndBlock(url) {
  const domain = new URL(url).hostname;

  const existingRules = await chrome.declarativeNetRequest.getDynamicRules();
  if (existingRules.some(rule => rule.condition.urlFilter === domain)) return;

  try {
    const res = await fetch(`http://127.0.0.1:5000/check_and_classify?url=${domain}`);
    
    if (!res.ok) {
      const text = await res.text();
      console.error("Server error:", res.status, text);
      return;
    }

    const existingRules = await chrome.declarativeNetRequest.getDynamicRules();
    const usedIds = existingRules.map(rule => rule.id);
    const maxId = usedIds.length ? Math.max(...usedIds) : 0;
    const newRuleId = maxId + 1;
    const data = await res.json();

    if (data.block) {
      const newRule = {
        id: newRuleId,
        priority: 1,
        action: { type: "block" },
        condition: {
          urlFilter: domain,
          resourceTypes: ["main_frame"]
        }
      };

      // Add rule dynamically in Chrome — in-memory only
      await chrome.declarativeNetRequest.updateDynamicRules({
        addRules: [newRule]
      });

      console.log(`Blocked dynamically: ${domain}`);
    }
  } catch (e) {
    console.error("Error during classification:", e);
  }
}

// Load rules on extension installation or startup
chrome.runtime.onInstalled.addListener(loadInitialRules);
chrome.runtime.onStartup.addListener(loadInitialRules);

// Classify and block on page navigation
chrome.webNavigation.onBeforeNavigate.addListener(details => {
  classifyAndBlock(details.url);
}, {
  url: [{ schemes: ["http", "https"] }]
});
