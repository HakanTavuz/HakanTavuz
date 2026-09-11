/**
 * Local asset bootstrap — Python yokken SVG'leri basar.
 * GitHub Actions hâlâ Python pipeline'ı kullanır.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

const PROFILE = JSON.parse(fs.readFileSync(path.join(__dirname, "profile.json"), "utf8"));
const fromEnv = process.env.GH_PROFILE_USER;
const USERNAME =
  fromEnv && fromEnv !== "YOUR_USERNAME" ? fromEnv : PROFILE.username;
const DISPLAY_NAME = PROFILE.display_name;
const ROLE = PROFILE.role;
const LOCATION = PROFILE.location;
const INFO_ROWS = [
  ["Name", DISPLAY_NAME],
  ["Role", ROLE],
  ["Location", LOCATION],
  ...PROFILE.rows,
];

const RAMP = " .`:-=+*cs#%@";
const COLS = 100;
const ROWS = 53;
const CELL_W = 8;
const CELL_H = 15;
const WHITE_FLOOR = 0.8;
const PAD = 20;
const TITLEBAR_H = 30;
const STATUS_H = 30;
const ART_W = COLS * CELL_W;
const ART_H = ROWS * CELL_H;
const CANVAS_W = ART_W + PAD * 2;
const CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD;
const ROW_DUR = 0.11;
const STAGGER = 0.11;

function esc(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function proceduralRows() {
  const rows = [];
  for (let y = 0; y < ROWS; y++) {
    let line = "";
    const ny = (y / (ROWS - 1)) * 2 - 1;
    for (let x = 0; x < COLS; x++) {
      const nx = (x / (COLS - 1)) * 2 - 1;
      let lum = 1;
      const hx = 0.02;
      const hy = -0.18;
      const dx = (nx - hx) / 0.38;
      const dy = (ny - hy) / 0.5;
      const d = dx * dx + dy * dy;
      if (d < 1) {
        const edge = Math.max(0, 1 - d);
        let light = 0.28 + 0.5 * (0.55 - dx * 0.28 - dy * 0.42);
        light *= 0.55 + 0.45 * edge;
        if (ny < -0.22) light *= 0.32 + 0.25 * Math.max(0, ny + 0.55);
        for (const [ex, ey] of [
          [-0.13, -0.18],
          [0.15, -0.18],
        ]) {
          const ed = ((nx - ex) / 0.07) ** 2 + ((ny - ey) / 0.045) ** 2;
          if (ed < 1) light *= 0.22;
        }
        const nd = ((nx - 0.02) / 0.035) ** 2 + ((ny - 0.02) / 0.08) ** 2;
        if (nd < 1) light *= 0.55;
        if (nx > -0.08 && nx < 0.12 && ny > 0.18 && ny < 0.28) light *= 0.45;
        lum = Math.max(0.04, Math.min(0.92, light));
      }
      const sx = Math.abs(nx) / 0.72;
      const sy = (ny - 0.42) / 0.55;
      if (sy > 0 && sx * sx + sy * sy * 0.35 < 1 && d >= 1) lum = 0.18 + 0.12 * sx;
      if (lum >= WHITE_FLOOR) {
        line += " ";
        continue;
      }
      const idx = Math.max(0, Math.min(RAMP.length - 1, Math.round((1 - lum) * (RAMP.length - 1))));
      line += RAMP[idx];
    }
    rows.push(line);
  }
  return rows;
}

function portraitSvg(rowsTxt) {
  const user = USERNAME;
  const artTop = TITLEBAR_H + PAD * 0.35;
  const fontSize = CELL_H * 0.86;
  const parts = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${CANVAS_W}" height="${CANVAS_H}" viewBox="0 0 ${CANVAS_W} ${CANVAS_H}">`,
    `<rect width="${CANVAS_W}" height="${CANVAS_H}" rx="12" fill="#0d1117"/>`,
    `<rect x="1" y="1" width="${CANVAS_W - 2}" height="${CANVAS_H - 2}" rx="11" fill="none" stroke="#30363d"/>`,
    `<rect width="${CANVAS_W}" height="${TITLEBAR_H}" rx="12" fill="#111722"/>`,
    `<rect y="${TITLEBAR_H - 12}" width="${CANVAS_W}" height="12" fill="#111722"/>`,
  ];
  ["#ff5f56", "#ffbd2e", "#27c93f"].forEach((c, i) => {
    parts.push(`<circle cx="${18 + i * 16}" cy="${TITLEBAR_H / 2}" r="5" fill="${c}"/>`);
  });
  parts.push(
    `<text x="72" y="${TITLEBAR_H / 2 + 4}" fill="#7d8590" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${esc(user)}@github: ~$ ./portrait.sh</text>`,
  );
  parts.push("<defs>");
  rowsTxt.forEach((_, ry) => {
    const rowY = artTop + ry * CELL_H;
    const delay = ry * STAGGER;
    parts.push(
      `<clipPath id="wipe${ry}"><rect x="${PAD}" y="${rowY}" width="0" height="${CELL_H}"><animate attributeName="width" from="0" to="${ART_W}" dur="${ROW_DUR}s" begin="${delay.toFixed(3)}s" fill="freeze"/></rect></clipPath>`,
    );
  });
  parts.push("</defs>");
  rowsTxt.forEach((line, ry) => {
    const y = artTop + ry * CELL_H + CELL_H * 0.74;
    const delay = ry * STAGGER;
    parts.push(
      `<text x="${PAD}" y="${y.toFixed(2)}" fill="#c9d1d9" font-size="${fontSize.toFixed(2)}" xml:space="preserve" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" clip-path="url(#wipe${ry})">${esc(line)}</text>`,
    );
    parts.push(
      `<rect x="${PAD}" y="${(artTop + ry * CELL_H + 2).toFixed(2)}" width="7" height="${CELL_H - 4}" fill="#c9d1d9"><animate attributeName="x" from="${PAD}" to="${PAD + ART_W}" dur="${ROW_DUR}s" begin="${delay.toFixed(3)}s" fill="freeze"/><animate attributeName="opacity" from="1" to="0" dur="0.04s" begin="${(delay + ROW_DUR).toFixed(3)}s" fill="freeze"/></rect>`,
    );
  });
  const statusY = TITLEBAR_H + ART_H + PAD * 0.55 + 18;
  parts.push(`<rect y="${TITLEBAR_H + ART_H + PAD * 0.25}" width="${CANVAS_W}" height="${STATUS_H}" fill="#111722"/>`);
  parts.push(
    `<text x="${PAD}" y="${statusY.toFixed(2)}" fill="#7d8590" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${esc(user)}@github:~$ whoami  <tspan fill="#c9d1d9">${esc(DISPLAY_NAME)}</tspan></text>`,
  );
  parts.push(
    `<rect x="${PAD + 210}" y="${statusY - 11}" width="7" height="13" fill="#c9d1d9"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>`,
  );
  parts.push("</svg>");
  return parts.join("");
}

function infoCardSvg() {
  const user = USERNAME;
  const W = 490;
  const H = 360;
  const TITLEBAR_H2 = 36;
  const LINE_H = 28;
  const parts = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`,
    `<rect width="${W}" height="${H}" rx="10" fill="#0d1117"/>`,
    `<rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="9" fill="none" stroke="#30363d"/>`,
    `<rect width="${W}" height="${TITLEBAR_H2}" rx="10" fill="#111722"/>`,
    `<rect y="${TITLEBAR_H2 - 10}" width="${W}" height="10" fill="#111722"/>`,
  ];
  ["#ff5f57", "#febc2e", "#28c840"].forEach((c, i) => {
    parts.push(`<circle cx="${20 + i * 20}" cy="${TITLEBAR_H2 / 2 + 1}" r="6" fill="${c}"/>`);
  });
  parts.push(
    `<text x="88" y="${TITLEBAR_H2 / 2 + 5}" fill="#7d8590" font-size="13" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${esc(user)}@github:~</text>`,
  );
  parts.push(`<line x1="0" y1="${TITLEBAR_H2 + 1}" x2="${W}" y2="${TITLEBAR_H2 + 1}" stroke="#30363d"/>`);
  const contentY = TITLEBAR_H2 + 32;
  INFO_ROWS.forEach(([label, value], i) => {
    const y = contentY + i * LINE_H;
    const begin = (i * 0.22).toFixed(2);
    parts.push(`<g transform="translate(28 ${y})" opacity="0">`);
    parts.push(`<animate attributeName="opacity" from="0" to="1" dur="0.38s" begin="${begin}s" fill="freeze"/>`);
    parts.push(
      `<animateTransform attributeName="transform" type="translate" from="42 ${y}" to="28 ${y}" dur="0.38s" begin="${begin}s" fill="freeze"/>`,
    );
    parts.push(
      `<text font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13"><tspan fill="#7ee787">${esc(label)}</tspan><tspan fill="#7d8590">  │  </tspan><tspan fill="#c9d1d9">${esc(value)}</tspan></text>`,
    );
    parts.push("</g>");
  });
  const colors = ["#ff5f57", "#febc2e", "#28c840", "#2ea5ff", "#a06cd5", "#ff6ac1"];
  const segW = (W - 56) / colors.length;
  colors.forEach((c, i) => {
    const x = 28 + i * segW;
    parts.push(`<rect x="${x.toFixed(2)}" y="${H - 18}" width="${(segW - 4).toFixed(2)}" height="4" rx="1" fill="${c}"/>`);
  });
  parts.push("</svg>");
  return parts.join("\n");
}

function fallbackDays() {
  const days = [];
  const start = new Date(Date.UTC(2025, 8, 7));
  const end = new Date(Date.UTC(2026, 8, 11));
  for (let d = new Date(start); d <= end; d.setUTCDate(d.getUTCDate() + 1)) {
    const date = d.toISOString().slice(0, 10);
    days.push({ date, count: date === "2026-09-10" ? 2 : 0 });
  }
  return days;
}

async function fetchDays(username) {
  const headers = { "User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)" };
  const api = `https://github-contributions-api.jogruber.de/v4/${encodeURIComponent(username)}?y=last`;
  const res = await fetch(api, { headers });
  if (!res.ok) throw new Error(`contrib fetch ${res.status}`);
  const data = await res.json();
  return data.contributions.map((c) => ({ date: c.date, count: c.count }));
}

function levelFor(count, maxCount) {
  if (count === 0) return 0;
  if (!maxCount) return 0;
  const ratio = count / maxCount;
  if (ratio <= 0.15) return 1;
  if (ratio <= 0.35) return 2;
  if (ratio <= 0.55) return 3;
  if (ratio <= 0.8) return 4;
  return 5;
}

function buildGrid(days) {
  const maxCount = Math.max(0, ...days.map((d) => d.count));
  const first = new Date(days[0].date + "T00:00:00Z");
  const jsDay = first.getUTCDay();
  let col = Array(jsDay).fill(null);
  const grid = [];
  for (const d of days) {
    const date = new Date(d.date + "T00:00:00Z");
    const weekday = date.getUTCDay();
    while (col.length < weekday) col.push(null);
    col.push([d.date, d.count, levelFor(d.count, maxCount)]);
    if (col.length === 7) {
      grid.push(col);
      col = [];
    }
  }
  if (col.length) {
    while (col.length < 7) col.push(null);
    grid.push(col);
  }
  return grid;
}

function heatmapSvg(days) {
  const PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"];
  const CELL = 12;
  const GAP = 3;
  const STEP = CELL + GAP;
  const PAD2 = 22;
  const LEFT = 30;
  const TOP = 20;
  const TB = 30;
  const grid = buildGrid(days);
  const nCols = grid.length;
  const artW = nCols * STEP;
  const artH = 7 * STEP;
  const canvasW = PAD2 + LEFT + artW + PAD2;
  const statsH = 88;
  const canvasH = TB + TOP + artH + statsH + PAD2;
  const user = USERNAME;
  const months = [];
  const seen = new Set();
  grid.forEach((column, ci) => {
    for (const cell of column) {
      if (!cell) continue;
      const date = new Date(cell[0] + "T00:00:00Z");
      const key = `${date.getUTCFullYear()}-${date.getUTCMonth()}`;
      if (!seen.has(key) && date.getUTCDate() <= 7) {
        seen.add(key);
        months.push([ci, date.toLocaleString("en-US", { month: "short", timeZone: "UTC" })]);
      }
      break;
    }
  });
  const total = days.reduce((a, d) => a + d.count, 0);
  let cur = 0;
  for (let i = days.length - 1; i >= 0; i--) {
    if (days[i].count === 0 && i === days.length - 1) continue;
    if (days[i].count > 0) cur++;
    else break;
  }
  let longest = 0;
  let run = 0;
  for (const d of days) {
    if (d.count > 0) {
      run++;
      longest = Math.max(longest, run);
    } else run = 0;
  }
  const best = days.reduce((a, b) => (b.count > a.count ? b : a));

  const css = `@keyframes cell{0%{opacity:0;transform:translateY(-6px)}100%{opacity:1;transform:translateY(0)}}.c{opacity:0;animation:cell 0.42s cubic-bezier(.2,.8,.2,1) both}@media (prefers-reduced-motion: reduce){.c{opacity:1;animation:none}}`;
  const parts = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${canvasW}" height="${canvasH}" viewBox="0 0 ${canvasW} ${canvasH}">`,
    `<style>${css}</style>`,
    `<rect width="${canvasW}" height="${canvasH}" rx="12" fill="#0a0e14"/>`,
    `<rect x="1" y="1" width="${canvasW - 2}" height="${canvasH - 2}" rx="11" fill="none" stroke="#30363d"/>`,
    `<rect width="${canvasW}" height="${TB}" rx="12" fill="#0d1420"/>`,
    `<rect y="${TB - 12}" width="${canvasW}" height="12" fill="#0d1420"/>`,
  ];
  ["#ff5f56", "#ffbd2e", "#27c93f"].forEach((c, i) => {
    parts.push(`<circle cx="${18 + i * 16}" cy="${TB / 2}" r="5" fill="${c}"/>`);
  });
  parts.push(
    `<text x="72" y="${TB / 2 + 4}" fill="#7d8590" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${esc(user)}@github: ~/contributions --graph</text>`,
  );
  const gridTop = TB + TOP;
  const gridLeft = PAD2 + LEFT;
  months.forEach(([ci, label]) => {
    parts.push(
      `<text x="${gridLeft + ci * STEP}" y="${TB + 16}" fill="#7d8590" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${label}</text>`,
    );
  });
  [
    [1, "Mon"],
    [3, "Wed"],
    [5, "Fri"],
  ].forEach(([wi, name]) => {
    const y = gridTop + wi * STEP + CELL * 0.78;
    parts.push(
      `<text x="${PAD2}" y="${y.toFixed(1)}" fill="#7d8590" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${name}</text>`,
    );
  });
  grid.forEach((column, ci) => {
    column.forEach((cell, ri) => {
      if (!cell) return;
      const [dateS, count, lvl] = cell;
      const gx = gridLeft + ci * STEP;
      const gy = gridTop + ri * STEP;
      const delay = ci * 0.018 + ri * 0.045;
      const plural = count === 1 ? "" : "s";
      parts.push(
        `<rect class="c" x="${gx}" y="${gy}" width="${CELL}" height="${CELL}" rx="2" fill="${PALETTE[lvl]}" style="animation-delay:${delay.toFixed(3)}s"><title>${dateS}: ${count} contribution${plural}</title></rect>`,
      );
    });
  });
  const legY = gridTop + artH + 6;
  const legX = canvasW - PAD2 - (PALETTE.length * (CELL - 1) + 70);
  parts.push(
    `<text x="${legX - 28}" y="${legY + 10}" fill="#7d8590" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">Less</text>`,
  );
  let lx = legX + 8;
  PALETTE.forEach((c) => {
    parts.push(`<rect x="${lx}" y="${legY}" width="${CELL - 2}" height="${CELL - 2}" rx="2" fill="${c}"/>`);
    lx += CELL;
  });
  parts.push(
    `<text x="${lx + 4}" y="${legY + 10}" fill="#7d8590" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">More</text>`,
  );
  const sepY = legY + CELL + 14;
  parts.push(`<line x1="${PAD2}" y1="${sepY}" x2="${canvasW - PAD2}" y2="${sepY}" stroke="#30363d"/>`);
  const ly = sepY + 24;
  parts.push(
    `<text x="${PAD2}" y="${ly}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13"><tspan fill="#39d353" font-weight="700">${total.toLocaleString("en-US")}</tspan><tspan fill="#e6edf3"> contributions in the last year</tspan></text>`,
  );
  parts.push(
    `<text x="${canvasW - PAD2}" y="${ly}" text-anchor="end" fill="#7d8590" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">${days[0].date} → ${days[days.length - 1].date}</text>`,
  );
  parts.push(
    `<text x="${PAD2}" y="${ly + 24}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" fill="#7d8590">current streak <tspan fill="#f2cc60">${cur} days</tspan>  ·  longest <tspan fill="#e6edf3">${longest} days</tspan></text>`,
  );
  parts.push(
    `<text x="${canvasW - PAD2}" y="${ly + 24}" text-anchor="end" fill="#7d8590" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">best day ${best.count} on ${best.date}</text>`,
  );
  parts.push("</svg>");
  return { svg: parts.join(""), total, days };
}

function writeReadme() {
  const user = USERNAME;
  return `<div align="center">
  <h3><code>${user}@github ~ $ ./contributions.sh</code></h3>
  <img src="./contrib-heatmap.svg" width="860" alt="contribution heatmap" />
  <br/><br/>
  <h3><code>${user}@github ~ $ whoami</code></h3>
  <table>
    <tr>
      <td valign="top"><img src="./portrait-ascii.svg" width="370" alt="ascii portrait" /></td>
      <td valign="top"><img src="./info-card.svg" width="490" alt="neofetch info card" /></td>
    </tr>
  </table>
  <p>${DISPLAY_NAME} · ${ROLE}</p>
</div>
`;
}

async function main() {
  fs.mkdirSync(path.join(ROOT, "data"), { recursive: true });
  const portrait = portraitSvg(proceduralRows());
  fs.writeFileSync(path.join(ROOT, "portrait-ascii.svg"), portrait);
  const card = infoCardSvg();
  fs.writeFileSync(path.join(ROOT, "info-card.svg"), card);
  let days;
  try {
    days = await fetchDays(USERNAME);
  } catch (err) {
    console.warn("live fetch failed:", err.message);
    days = fallbackDays();
  }
  const heat = heatmapSvg(days);
  fs.writeFileSync(path.join(ROOT, "contrib-heatmap.svg"), heat.svg);
  let current = 0;
  for (let i = days.length - 1; i >= 0; i--) {
    if (days[i].count === 0 && i === days.length - 1) continue;
    if (days[i].count > 0) current++;
    else break;
  }
  let longest = 0;
  let run = 0;
  for (const d of days) {
    if (d.count > 0) {
      run++;
      longest = Math.max(longest, run);
    } else run = 0;
  }
  const best = days.reduce((a, b) => (b.count > a.count ? b : a));
  fs.writeFileSync(
    path.join(ROOT, "data", "contributions.json"),
    JSON.stringify(
      {
        username: USERNAME,
        generated_at: new Date().toISOString(),
        range: { start: days[0].date, end: days[days.length - 1].date },
        total_contributions: heat.total,
        current_streak: { length: current },
        longest_streak: { length: longest },
        best_day: best,
        days,
      },
      null,
      2,
    ),
  );
  fs.writeFileSync(path.join(ROOT, "README.md"), writeReadme());
  console.log("portrait-ascii.svg", portrait.length);
  console.log("info-card.svg", card.length);
  console.log("contrib-heatmap.svg", heat.svg.length, "total", heat.total);
  console.log("README.md ready for", USERNAME);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
