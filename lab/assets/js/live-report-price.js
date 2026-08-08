(() => {
  const body = document.body;
  const ticker = body?.dataset?.stockTicker;
  const source = body?.dataset?.priceSource;
  if (!ticker || !source) return;
  fetch(source, { cache: "no-store" })
    .then((response) => response.ok ? response.json() : null)
    .then((payload) => {
      const prices = payload?.prices || {};
      const entry = Object.values(prices).find((item) => item?.symbol?.replace(".T", "") === ticker || item?.symbol === `${ticker}.T`);
      if (!entry || !Number.isFinite(Number(entry.price))) return;
      const formatter = new Intl.NumberFormat("ja-JP", {
        style: "currency",
        currency: entry.currency || "JPY",
        maximumFractionDigits: entry.currency === "JPY" ? 0 : 2
      });
      document.querySelectorAll("[data-live-price]").forEach((node) => { node.textContent = formatter.format(Number(entry.price)); });
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
