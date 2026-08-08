const DATA_URL = "./data/stocks.json";
const PRICE_URL = "./data/prices.json";
const SIGNAL_URL = "./data/signals.json";

const state = {
  stocks: [],
  prices: {},
  signals: {},
  market: "all",
  query: "",
  sort: "default",
  view: "card"
};

const compactMediaQuery = window.matchMedia("(max-width: 760px)");

const elements = {
  results: document.querySelector("#stock-results"),
  resultStatus: document.querySelector("#result-status"),
  search: document.querySelector("#stock-search"),
  filters: document.querySelector("#market-filters"),
  sort: document.querySelector("#stock-sort"),
  cardView: document.querySelector("#card-view"),
  listView: document.querySelector("#list-view"),
  totalCount: document.querySelector("#total-count"),
  japanCount: document.querySelector("#japan-count"),
  usCount: document.querySelector("#us-count"),
  priceSummary: document.querySelector("#price-summary")
};

function formatPrice(value, currency) {
  if (!Number.isFinite(value)) return "取得準備中";
  return new Intl.NumberFormat("ja-JP", {
    style: "currency",
    currency,
    maximumFractionDigits: currency === "JPY" ? 0 : 2
  }).format(value);
}

function formatChange(price) {
  if (!Number.isFinite(price?.change) || !Number.isFinite(price?.changePct)) return "前日比 —";
  const sign = price.change > 0 ? "+" : "";
  const digits = price.currency === "JPY" ? 0 : 2;
  return `${sign}${price.change.toFixed(digits)} (${sign}${price.changePct.toFixed(2)}%)`;
}

function formatDate(value) {
  if (!value) return "株価未取得";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

function getSignal(stockId) {
  const source = state.signals[stockId];
  const position = Number(source?.position);
  const allowedZones = ["売られすぎ", "中立", "買われすぎ"];
  if (!Number.isFinite(position) || !allowedZones.includes(source?.zone)) {
    return { position: 50, zone: "判定準備中", asOf: null, pending: true };
  }
  return {
    position: Math.min(100, Math.max(0, position)),
    zone: source.zone,
    asOf: source.asOf || null,
    pending: false
  };
}

function reportLink(report, number, label, compact = false) {
  const available = Boolean(report?.available && report?.path);
  const link = document.createElement(available ? "a" : "span");
  link.className = `report-link${available ? "" : " is-disabled"}`;
  if (available) link.href = report.path;
  else {
    link.setAttribute("aria-disabled", "true");
    link.title = "レポート準備中";
  }
  const numberLabel = compact ? number : `REPORT ${number}`;
  link.innerHTML = `<small>${numberLabel}</small><span>${label}${available ? " →" : "（準備中）"}</span>`;
  return link;
}

function createCard(stock) {
  const price = state.prices[stock.id] || null;
  const signal = getSignal(stock.id);
  const card = document.createElement("article");
  card.className = "stock-card";

  const head = document.createElement("div");
  head.className = "card-head";
  const identity = document.createElement("div");
  const ticker = document.createElement("p");
  ticker.className = "ticker";
  ticker.textContent = stock.ticker;
  const name = document.createElement("h3");
  name.className = "company-name";
  name.textContent = stock.name;
  const englishName = document.createElement("p");
  englishName.className = "company-name-en";
  englishName.textContent = stock.nameEn;
  identity.append(ticker, name, englishName);
  const badge = document.createElement("span");
  badge.className = "market-badge";
  badge.textContent = stock.marketLabel;
  head.append(identity, badge);

  const sector = document.createElement("p");
  sector.className = "sector";
  sector.textContent = stock.sector;

  const changeClass = Number(price?.change) > 0 ? " is-positive" : Number(price?.change) < 0 ? " is-negative" : "";
  const pricePanel = document.createElement("div");
  pricePanel.className = "price-panel";
  pricePanel.innerHTML = `
    <div><span class="metric-label">現在株価</span><strong class="price-value">${formatPrice(Number(price?.price), stock.currency)}</strong><small class="price-date">${formatDate(price?.marketTime)}</small></div>
    <div><span class="metric-label">前日比</span><strong class="change-value${changeClass}">${formatChange(price)}</strong><small class="price-date">${price?.status === "stale" ? "前回の正常値を表示中" : "終値ベース"}</small></div>`;

  const signalBlock = document.createElement("div");
  signalBlock.className = "signal-block";
  signalBlock.innerHTML = `
    <div class="signal-heading"><span>レポート総合判定</span><strong>${signal.zone}</strong></div>
    <div class="signal-track" aria-label="レポート総合判定 ${signal.zone}"><span class="signal-marker${signal.pending ? " is-pending" : ""}" style="left:${signal.position}%"></span></div>
    <div class="signal-scale"><span>売られすぎ</span><span>中立</span><span>買われすぎ</span></div>
    <p class="signal-zone">${signal.asOf ? `分析基準日：${signal.asOf}` : "3つのレポート作成後に判定します"}</p>`;

  const actions = document.createElement("div");
  actions.className = "card-actions";
  actions.append(
    reportLink(stock.reports.company, "01", "企業について"),
    reportLink(stock.reports.valuation, "02", "現在の株価"),
    reportLink(stock.reports.catalysts, "03", "今後のカタリスト")
  );

  card.append(head, sector, pricePanel, signalBlock, actions);
  return card;
}

function closeOtherCompactRows(currentRow) {
  document.querySelectorAll(".stock-row.is-expanded").forEach((row) => {
    if (row === currentRow) return;
    const toggle = row.querySelector(".stock-row-toggle");
    const details = row.querySelector(".stock-row-details");
    row.classList.remove("is-expanded");
    if (toggle) {
      toggle.textContent = "+";
      toggle.setAttribute("aria-expanded", "false");
    }
    if (details) details.hidden = true;
  });
}

function createCompactRow(stock) {
  const price = state.prices[stock.id] || null;
  const signal = getSignal(stock.id);
  const row = document.createElement("article");
  row.className = "stock-row stock-row-compact";

  const summary = document.createElement("div");
  summary.className = "stock-row-summary";

  const identity = document.createElement("div");
  identity.className = "stock-row-identity";
  const ticker = document.createElement("strong");
  ticker.textContent = stock.ticker;
  const name = document.createElement("span");
  name.textContent = stock.name;
  identity.append(ticker, name);

  const priceCell = document.createElement("div");
  priceCell.className = "stock-row-price";
  const priceLabel = document.createElement("small");
  priceLabel.textContent = "現在株価";
  const priceStrong = document.createElement("strong");
  priceStrong.textContent = formatPrice(Number(price?.price), stock.currency);
  priceCell.append(priceLabel, priceStrong);

  const toggle = document.createElement("button");
  toggle.className = "stock-row-toggle";
  toggle.type = "button";
  toggle.textContent = "+";
  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-label", `${stock.ticker}の詳細を開く`);

  summary.append(identity, priceCell, toggle);

  const details = document.createElement("div");
  details.className = "stock-row-details";
  details.hidden = true;

  const tags = document.createElement("div");
  tags.className = "stock-row-tags";
  const market = document.createElement("span");
  market.textContent = stock.marketLabel;
  const sector = document.createElement("span");
  sector.textContent = stock.sector;
  const date = document.createElement("span");
  date.textContent = `${formatDate(price?.marketTime)} 更新`;
  tags.append(market, sector, date);

  const detailGrid = document.createElement("div");
  detailGrid.className = "stock-row-detail-grid";
  detailGrid.innerHTML = `
    <div>
      <small>前日比</small>
      <strong>${formatChange(price)}</strong>
    </div>
    <div>
      <small>レポート判定</small>
      <strong>${signal.zone}</strong>
    </div>`;

  const signalNote = document.createElement("p");
  signalNote.className = "stock-row-note";
  signalNote.textContent = signal.asOf ? `分析基準日：${signal.asOf}` : "3つのレポート作成後に判定します";

  const actions = document.createElement("div");
  actions.className = "stock-row-actions";
  actions.append(
    reportLink(stock.reports.company, "01", "企業について"),
    reportLink(stock.reports.valuation, "02", "現在の株価"),
    reportLink(stock.reports.catalysts, "03", "今後のカタリスト")
  );

  details.append(tags, detailGrid, signalNote, actions);
  row.append(summary, details);

  toggle.addEventListener("click", () => {
    const nextExpanded = !row.classList.contains("is-expanded");
    closeOtherCompactRows(row);
    row.classList.toggle("is-expanded", nextExpanded);
    details.hidden = !nextExpanded;
    toggle.textContent = nextExpanded ? "−" : "+";
    toggle.setAttribute("aria-expanded", String(nextExpanded));
    toggle.setAttribute("aria-label", `${stock.ticker}の詳細を${nextExpanded ? "閉じる" : "開く"}`);
  });

  return row;
}

function createList(stocks, compact = false) {
  const list = document.createElement("div");
  list.className = "stock-list";
  stocks.forEach((stock) => {
    if (compact) {
      list.append(createCompactRow(stock));
      return;
    }
    const price = state.prices[stock.id] || null;
    const signal = getSignal(stock.id);
    const row = document.createElement("article");
    row.className = "stock-row";

    const identity = document.createElement("div");
    identity.className = "stock-row-identity";
    const ticker = document.createElement("strong");
    ticker.textContent = stock.ticker;
    const name = document.createElement("span");
    name.textContent = stock.name;
    identity.append(ticker, name);

    const market = document.createElement("span");
    market.className = "stock-row-market";
    market.textContent = stock.marketLabel;

    const priceCell = document.createElement("div");
    priceCell.className = "stock-row-price";
    const priceStrong = document.createElement("strong");
    priceStrong.textContent = formatPrice(Number(price?.price), stock.currency);
    const priceSmall = document.createElement("small");
    priceSmall.textContent = formatChange(price);
    priceCell.append(priceStrong, priceSmall);

    const signalCell = document.createElement("div");
    signalCell.className = "stock-row-signal";
    const signalStrong = document.createElement("strong");
    signalStrong.textContent = signal.zone;
    const signalSmall = document.createElement("small");
    signalSmall.textContent = "レポート判定";
    signalCell.append(signalStrong, signalSmall);

    const actions = document.createElement("div");
    actions.className = "stock-row-actions";
    actions.append(
      reportLink(stock.reports.company, "01", "企業", true),
      reportLink(stock.reports.valuation, "02", "株価", true),
      reportLink(stock.reports.catalysts, "03", "材料", true)
    );
    row.append(identity, market, priceCell, signalCell, actions);
    list.append(row);
  });
  return list;
}

function visibleStocks() {
  const query = state.query.trim().toLocaleLowerCase("ja");
  const filtered = state.stocks.filter((stock) => {
    const marketMatch = state.market === "all" || stock.market === state.market;
    const searchable = [stock.ticker, stock.quoteSymbol, stock.name, stock.nameEn, stock.sector, stock.marketLabel].join(" ").toLocaleLowerCase("ja");
    return marketMatch && searchable.includes(query);
  });

  return filtered.sort((a, b) => {
    if (state.sort === "name") return a.name.localeCompare(b.name, "ja");
    if (state.sort === "price-desc") return (Number(state.prices[b.id]?.price) || -Infinity) - (Number(state.prices[a.id]?.price) || -Infinity);
    if (state.sort === "signal-asc") return (Number(state.signals[a.id]?.position) || Infinity) - (Number(state.signals[b.id]?.position) || Infinity);
    if (state.sort === "signal-desc") return (Number(state.signals[b.id]?.position) || -Infinity) - (Number(state.signals[a.id]?.position) || -Infinity);
    return a.order - b.order;
  });
}

function render() {
  const stocks = visibleStocks();
  const compact = compactMediaQuery.matches;
  elements.results.replaceChildren();
  elements.resultStatus.textContent = `${stocks.length}件を表示`;
  elements.results.className = !compact && state.view === "card" ? "stock-grid" : "";

  if (!stocks.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "条件に一致する銘柄がありません。";
    elements.results.append(empty);
    return;
  }

  if (compact || state.view === "list") elements.results.append(createList(stocks, compact));
  else stocks.forEach((stock) => elements.results.append(createCard(stock)));
}

function updateSummary(pricePayload) {
  elements.totalCount.textContent = state.stocks.length;
  elements.japanCount.textContent = state.stocks.filter((stock) => stock.market === "JP").length;
  elements.usCount.textContent = state.stocks.filter((stock) => stock.market === "US").length;
  elements.priceSummary.textContent = pricePayload.generatedAt
    ? `株価データ更新：${formatDate(pricePayload.generatedAt)}`
    : "株価データは初回更新前です";
}

function showLoadError(error) {
  console.error(error);
  elements.resultStatus.textContent = "読み込みに失敗しました";
  const panel = document.createElement("p");
  panel.className = "error-state";
  panel.textContent = "銘柄データを読み込めませんでした。時間をおいて再度お試しください。";
  elements.results.replaceChildren(panel);
}

async function init() {
  try {
    const [stockResponse, priceResponse, signalResponse] = await Promise.all([
      fetch(`${DATA_URL}?v=${Date.now()}`, { cache: "no-store" }),
      fetch(`${PRICE_URL}?v=${Date.now()}`, { cache: "no-store" }),
      fetch(`${SIGNAL_URL}?v=${Date.now()}`, { cache: "no-store" })
    ]);
    if (!stockResponse.ok || !priceResponse.ok || !signalResponse.ok) throw new Error("Data request failed");
    const stockPayload = await stockResponse.json();
    const pricePayload = await priceResponse.json();
    const signalPayload = await signalResponse.json();
    state.stocks = Array.isArray(stockPayload.stocks) ? stockPayload.stocks : [];
    state.prices = pricePayload.prices || {};
    state.signals = signalPayload.signals || {};
    updateSummary(pricePayload);
    render();
  } catch (error) {
    showLoadError(error);
  }
}

elements.search.addEventListener("input", (event) => {
  state.query = event.target.value;
  render();
});

elements.filters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-market]");
  if (!button) return;
  state.market = button.dataset.market;
  elements.filters.querySelectorAll("[data-market]").forEach((item) => {
    const active = item === button;
    item.classList.toggle("is-active", active);
    item.setAttribute("aria-pressed", String(active));
  });
  render();
});

elements.sort.addEventListener("change", (event) => {
  state.sort = event.target.value;
  render();
});

function setView(view) {
  state.view = view;
  const cardActive = view === "card";
  elements.cardView.classList.toggle("is-active", cardActive);
  elements.listView.classList.toggle("is-active", !cardActive);
  elements.cardView.setAttribute("aria-pressed", String(cardActive));
  elements.listView.setAttribute("aria-pressed", String(!cardActive));
  render();
}

elements.cardView.addEventListener("click", () => setView("card"));
elements.listView.addEventListener("click", () => setView("list"));

if (compactMediaQuery.addEventListener) {
  compactMediaQuery.addEventListener("change", render);
} else {
  compactMediaQuery.addListener(render);
}

init();
