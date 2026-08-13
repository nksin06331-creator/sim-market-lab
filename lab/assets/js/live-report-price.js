(() => {
  const body = document.body;
  const ticker = body?.dataset?.stockTicker;
  const source = body?.dataset?.priceSource;
  if (!ticker || !source) return;

  function parseScenarioPrice(text) {
    if (!text) return null;
    const normalized = String(text).replace(/,/g, "").replace(/[^\d.-]/g, "");
    const value = Number(normalized);
    return Number.isFinite(value) ? value : null;
  }

  function clampPercent(value) {
    if (!Number.isFinite(value)) return null;
    return Math.min(100, Math.max(0, value));
  }

  function updateValuationPosition(price) {
    const labels = Array.from(document.querySelectorAll(".position-labels span"));
    if (labels.length < 3) return;
    const bear = parseScenarioPrice(labels[0].textContent);
    const bull = parseScenarioPrice(labels[2].textContent);
    if (!Number.isFinite(bear) || !Number.isFinite(bull) || bear === bull) return;

    const position = clampPercent(((price - bear) / (bull - bear)) * 100);
    if (!Number.isFinite(position)) return;
    const positionText = `${position.toFixed(1)}%`;
    const scoreText = String(Math.round(position));

    document.querySelectorAll(".position-line .pin").forEach((pin) => {
      pin.style.left = positionText;
      pin.setAttribute("aria-label", `現在株価の位置 ${positionText}`);
    });

    const snapshot = document.querySelector("#snapshot");
    const positionParagraph = snapshot?.querySelector(".grid-2 > div:first-child p:not(.lead)");
    const positionValue = positionParagraph?.querySelector("b");
    if (positionValue) positionValue.textContent = positionText;

    const marketCompare = snapshot?.querySelector(".compare > div:first-child");
    const marketLabel = marketCompare?.querySelector("b");
    const marketMeter = marketCompare?.querySelector(".meter i");
    if (marketLabel) marketLabel.textContent = `今の株価 ${scoreText}/100`;
    if (marketMeter) marketMeter.style.width = `${Math.round(position)}%`;
  }

  fetch(source, { cache: "no-store" })
    .then((response) => response.ok ? response.json() : null)
    .then((payload) => {
      const prices = payload?.prices || {};
      const entry = Object.values(prices).find((item) => item?.symbol?.replace(".T", "") === ticker || item?.symbol === `${ticker}.T`);
      if (!entry || !Number.isFinite(Number(entry.price))) return;
      const price = Number(entry.price);
      const formatter = new Intl.NumberFormat("ja-JP", {
        style: "currency",
        currency: entry.currency || "JPY",
        maximumFractionDigits: entry.currency === "JPY" ? 0 : 2
      });
      document.querySelectorAll("[data-live-price]").forEach((node) => { node.textContent = formatter.format(price); });
      updateValuationPosition(price);
      if (entry.marketTime) {
        const date = new Intl.DateTimeFormat("ja-JP", {
          timeZone: "Asia/Tokyo",
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit"
        }).format(new Date(entry.marketTime));
        document.querySelectorAll("[data-live-price-date]").forEach((node) => { node.textContent = `${date}（分析基準値）`; });
      }
    })
    .catch(() => {});
})();
