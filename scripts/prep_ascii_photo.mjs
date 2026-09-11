/**
 * Fotoğraf → ASCII grid. prep_photo.py + make_ascii_svg.py'nin Node karşılığı.
 * rembg yok; yüz elipsi + kontrast ile arka planı boşaltır.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

export const COLS = 100;
export const ROWS = 53;
export const RAMP = " .`:-=+*cs#%@";
export const GAMMA = 1.18;
export const WHITE_FLOOR = 0.8;
export const CONTRAST = 1.15;

function lumaToChar(lum) {
  if (lum >= WHITE_FLOOR) return " ";
  const idx = Math.max(0, Math.min(RAMP.length - 1, Math.round((1 - lum) * (RAMP.length - 1))));
  return RAMP[idx];
}

export async function prepPhoto(inputPath, outputPng) {
  const img = sharp(inputPath);
  const meta = await img.metadata();
  const w = meta.width;
  const h = meta.height;

  // selfie: kafayı + omuzları al, gökyüzü/yolu kes
  const left = Math.round(w * 0.08);
  const top = Math.round(h * 0.1);
  const cropW = Math.round(w * 0.84);
  const cropH = Math.round(h * 0.9);

  const buf = await sharp(inputPath)
    .extract({ left, top, width: cropW, height: cropH })
    .greyscale()
    .normalise()
    .linear(CONTRAST, -(CONTRAST - 1) * 128)
    .gamma(GAMMA)
    .resize(COLS, ROWS, { fit: "fill", kernel: sharp.kernel.lanczos3 })
    .raw()
    .toBuffer();

  const out = Buffer.alloc(COLS * ROWS);
  for (let y = 0; y < ROWS; y++) {
    const ny = (y / (ROWS - 1)) * 2 - 1;
    for (let x = 0; x < COLS; x++) {
      const nx = (x / (COLS - 1)) * 2 - 1;
      const i = y * COLS + x;
      let v = buf[i];

      // kafa + omuz maskesi: dışı beyaz (ASCII space)
      const head = ((nx - 0.02) / 0.52) ** 2 + ((ny + 0.12) / 0.62) ** 2;
      const shoulders = (Math.abs(nx) / 0.82) ** 2 + ((ny - 0.55) / 0.62) ** 2;
      let mask = 0;
      if (head < 1) mask = Math.max(mask, 1 - Math.max(0, head - 0.72) / 0.28);
      if (ny > 0.15 && shoulders < 1) mask = Math.max(mask, 0.85 * (1 - Math.max(0, shoulders - 0.7) / 0.3));
      mask = Math.max(0, Math.min(1, mask));

      const mixed = v * mask + 255 * (1 - mask);
      out[i] = Math.max(0, Math.min(255, Math.round(mixed)));
    }
  }

  await sharp(out, { raw: { width: COLS, height: ROWS, channels: 1 } })
    .png()
    .toFile(outputPng);

  return out;
}

export function gridFromLuma(buf) {
  const rows = [];
  for (let y = 0; y < ROWS; y++) {
    let line = "";
    for (let x = 0; x < COLS; x++) {
      const lum = buf[y * COLS + x] / 255;
      line += lumaToChar(lum);
    }
    rows.push(line);
  }
  return rows;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const src = path.join(ROOT, "source-photo.jpg");
  const prepped = path.join(ROOT, "source-prepped.png");
  const buf = await prepPhoto(src, prepped);
  const rows = gridFromLuma(buf);
  fs.writeFileSync(path.join(ROOT, "ascii-preview.txt"), rows.join("\n"));
  console.log("wrote", prepped);
  console.log(rows.filter((_, i) => i % 2 === 0).join("\n"));
}
