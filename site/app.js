/* ================= Momoro gallery app ================= */
const CONFIG = {
  projectName: "Momoro",
  githubUrl: "https://github.com/lyx-27/momoro",
};

const I18N = {
  en: {
    github: "View on GitHub", collection: "My Collection", random: "Surprise me", browse: "Browse all",
    empty: "Nothing here yet", emptyFav: "No favorites yet — tap the heart on any mascot to save it here.",
    download: "Download", fav: "Save", faved: "Saved",
    like: "Love it", dislike: "Nope", lang: "中文", footer: "Cute mascot avatars",
    dark: "Dark", light: "Light",
  },
  zh: {
    github: "在 GitHub 查看", collection: "我的收藏", random: "随机抽取", browse: "浏览全部",
    empty: "这里还没有内容", emptyFav: "还没有收藏 —— 点任意头像上的爱心即可收藏到这里。",
    download: "下载原图", fav: "收藏", faved: "已收藏",
    like: "喜欢", dislike: "不喜欢", lang: "EN", footer: "可爱吉祥物头像",
    dark: "深色", light: "浅色",
  },
};

const FAV_KEY = "momoro.favs";
const LANG_KEY = "momoro.lang";
const THEME_KEY = "momoro.theme";

const state = {
  items: [], view: [],
  lang: localStorage.getItem(LANG_KEY) || (navigator.language.startsWith("zh") ? "zh" : "en"),
  theme: localStorage.getItem(THEME_KEY) || (window.matchMedia && matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"),
  favOnly: false,
  favs: new Set(JSON.parse(localStorage.getItem(FAV_KEY) || "[]")),
  lbMode: "browse", lbIndex: -1, drawItem: null,
};

const $ = s => document.querySelector(s);
const t = () => I18N[state.lang];
const rand = n => Math.floor(Math.random() * n);
const heartSVG = '<svg class="ico"><use href="#i-heart"/></svg>';

/* ---------- favorites ---------- */
function saveFavs() { localStorage.setItem(FAV_KEY, JSON.stringify([...state.favs])); }
function isFav(id) { return state.favs.has(id); }
function toggleFav(id) { state.favs.has(id) ? state.favs.delete(id) : state.favs.add(id); saveFavs(); updateFavBadge(); }
function updateFavBadge() {
  const b = $("#favBadge");
  b.textContent = state.favs.size;
  b.style.display = state.favs.size ? "inline-flex" : "none";
}

/* ---------- grid ---------- */
function computeView() { state.view = state.items.filter(it => !state.favOnly || isFav(it.id)); }
function renderGrid() {
  computeView();
  $("#grid").innerHTML = state.view.map((it, i) => `
    <div class="card" style="--acc:${it.accent}" data-i="${i}">
      <button class="fav ${isFav(it.id) ? "on" : ""}" data-fav="${it.id}" aria-label="favorite">${heartSVG}</button>
      <div class="thumb"><img loading="lazy" src="${it.thumb}" alt="${it.name}"></div>
      <div class="cap">${it.name}</div>
    </div>`).join("");
  const empty = $("#empty");
  if (!state.view.length) { empty.textContent = state.favOnly ? t().emptyFav : t().empty; empty.classList.add("show"); }
  else empty.classList.remove("show");
}
function setCollection(on) {
  state.favOnly = on;
  $("#collBtn").classList.toggle("active", on);
  renderGrid();
}

/* ---------- detail modal ---------- */
function curItem() { return state.lbMode === "random" ? state.drawItem : state.view[state.lbIndex]; }
function openBrowse(i) {
  state.lbMode = "browse"; state.lbIndex = i;
  $("#lb").classList.remove("mode-random"); $("#lb").classList.add("open");
  document.body.style.overflow = "hidden"; renderDetail();
}
function openRandom() {
  state.lbMode = "random"; state.drawItem = state.items[rand(state.items.length)];
  $("#lb").classList.add("mode-random", "open");
  document.body.style.overflow = "hidden"; renderDetail();
}
function drawNext() {
  if (state.items.length < 2) return renderDetail();
  let it, id = state.drawItem && state.drawItem.id;
  do { it = state.items[rand(state.items.length)]; } while (it.id === id);
  state.drawItem = it; renderDetail();
}
function step(d) { if (!state.view.length) return; state.lbIndex = (state.lbIndex + d + state.view.length) % state.view.length; renderDetail(); }
function closeLb() { $("#lb").classList.remove("open"); document.body.style.overflow = ""; }
function renderDetail() {
  const it = curItem(); if (!it) return;
  $("#lb").style.setProperty("--acc", it.accent);
  const img = $("#lbImg"); img.src = it.thumb; img.alt = it.name;
  img.style.animation = "none"; void img.offsetWidth; img.style.animation = "";
  $("#lbName").textContent = it.name;
  $("#lbCat").textContent = it.category;
  const dl = $("#lbDownload"); dl.href = it.full; dl.setAttribute("download", it.id + ".png");
  $("#lbDlText").textContent = t().download;
  const fav = $("#lbFav"); fav.classList.toggle("on", isFav(it.id));
  fav.querySelector(".lbl").textContent = isFav(it.id) ? t().faved : t().fav;
  $("#btnLike").classList.toggle("on", isFav(it.id));
  if (state.lbMode === "browse")
    $("#lbCounter").textContent = `${state.lbIndex + 1} / ${state.view.length}`;
}

/* ---------- theme ---------- */
function updateThemeBtn() {
  $("#themeUse").setAttribute("href", state.theme === "dark" ? "#i-sun" : "#i-moon");
  $("#themeText").textContent = state.theme === "dark" ? t().light : t().dark;
}
function applyTheme() {
  document.documentElement.setAttribute("data-theme", state.theme);
  updateThemeBtn();
}

/* ---------- i18n ---------- */
function applyLang() {
  document.documentElement.lang = state.lang === "zh" ? "zh" : "en";
  $("#ghText").textContent = t().github;
  $("#collText").textContent = t().collection;
  $("#langText").textContent = t().lang;
  $("#randomText").textContent = t().random;
  $("#dislikeText").textContent = t().dislike;
  $("#likeText").textContent = t().like;
  $("#footer").textContent = t().footer;
  updateThemeBtn();
  renderGrid();
  if ($("#lb").classList.contains("open")) renderDetail();
}

/* ---------- events ---------- */
function wire() {
  $("#randomBtn").addEventListener("click", openRandom);
  $("#collBtn").addEventListener("click", () => setCollection(!state.favOnly));
  $("#langBtn").addEventListener("click", () => {
    state.lang = state.lang === "zh" ? "en" : "zh"; localStorage.setItem(LANG_KEY, state.lang); applyLang();
  });
  $("#themeBtn").addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark"; localStorage.setItem(THEME_KEY, state.theme); applyTheme();
  });

  $("#grid").addEventListener("click", e => {
    const favBtn = e.target.closest("[data-fav]");
    if (favBtn) {
      e.stopPropagation(); toggleFav(favBtn.dataset.fav);
      if (state.favOnly) renderGrid();
      else favBtn.classList.toggle("on", isFav(favBtn.dataset.fav));
      return;
    }
    const card = e.target.closest(".card"); if (card) openBrowse(+card.dataset.i);
  });

  // modal
  $("#lbClose").addEventListener("click", closeLb);
  $("#lbBackdrop").addEventListener("click", closeLb);
  $("#lbPrev").addEventListener("click", () => step(-1));
  $("#lbNext").addEventListener("click", () => step(1));
  $("#btnDislike").addEventListener("click", drawNext);
  $("#btnLike").addEventListener("click", () => {
    const it = curItem(); if (it && !isFav(it.id)) toggleFav(it.id);
    drawNext();
  });
  $("#lbFav").addEventListener("click", () => {
    const it = curItem(); if (!it) return;
    toggleFav(it.id); renderDetail();
    if (state.lbMode === "browse" && state.favOnly) {
      renderGrid();
      if (!state.view.length) return closeLb();
      state.lbIndex = Math.min(state.lbIndex, state.view.length - 1); renderDetail();
    }
  });
  document.addEventListener("keydown", e => {
    if (!$("#lb").classList.contains("open")) return;
    if (e.key === "Escape") closeLb();
    else if (state.lbMode === "browse" && e.key === "ArrowLeft") step(-1);
    else if (state.lbMode === "browse" && e.key === "ArrowRight") step(1);
  });
}

/* ---------- boot ---------- */
async function boot() {
  $("#ghLink").href = CONFIG.githubUrl;
  $("#brandName").textContent = CONFIG.projectName;
  document.title = CONFIG.projectName;
  try { state.items = await (await fetch("data/mascots.json")).json(); }
  catch (err) { $("#empty").textContent = "Could not load mascots.json (serve over http)."; $("#empty").classList.add("show"); return; }
  wire(); applyTheme(); updateFavBadge(); applyLang(); setCollection(false);
}
boot();
