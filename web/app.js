import { sequence, wrapValue } from "./game.js";

const canvas = document.querySelector("#circle-canvas");
const context = canvas.getContext("2d");
const canvasContainer = document.querySelector("#canvas-container");
const popup = document.querySelector("#point-popup");
const maxNInput = document.querySelector("#max-n");
const nSlider = document.querySelector("#n-slider");
const nValue = document.querySelector("#n-value");
const aInput = document.querySelector("#a-value");
const bInput = document.querySelector("#b-value");
const traverseButton = document.querySelector("#traverse-button");
const nextButton = document.querySelector("#next-button");
const minusButton = document.querySelector("#minus-button");
const plusButton = document.querySelector("#plus-button");

let traverseActive = false;
let traverseStep = 0;

function parseIntOrReset(input, fallback) {
  const value = Number.parseInt(input.value.trim(), 10);
  if (Number.isNaN(value)) {
    input.value = String(fallback);
    return fallback;
  }
  return value;
}

function maxN() {
  const value = Math.max(1, parseIntOrReset(maxNInput, 24));
  maxNInput.value = String(value);
  nSlider.max = String(value);
  if (Number(nSlider.value) > value) {
    nSlider.value = String(value);
  }
  return value;
}

function params() {
  const upper = maxN();
  const n = Math.min(upper, Math.max(1, Number(nSlider.value)));
  nSlider.value = String(n);
  nValue.textContent = String(n);
  return {
    n,
    a: parseIntOrReset(aInput, 2),
    b: parseIntOrReset(bInput, 1),
  };
}

function pointPosition(index, n, center, radius) {
  const angle = (2 * Math.PI * (index - 1)) / n - Math.PI / 2;
  return {
    x: center + radius * Math.cos(angle),
    y: center + radius * Math.sin(angle),
  };
}

function setPopup(value, point, size) {
  popup.textContent = `x = ${value}`;
  popup.hidden = false;
  popup.style.left = `${Math.min(size - popup.offsetWidth, Math.max(0, point.x - popup.offsetWidth / 2))}px`;
  popup.style.top = `${Math.min(size - popup.offsetHeight, Math.max(0, point.y - popup.offsetHeight - 22))}px`;
}

function render() {
  const { n, a, b } = params();
  const size = canvasContainer.clientWidth;
  const ratio = window.devicePixelRatio || 1;
  const center = size / 2;
  const radius = Math.max(1, size / 2 - Math.min(48, size * 0.12));
  canvas.width = Math.max(1, Math.round(size * ratio));
  canvas.height = Math.max(1, Math.round(size * ratio));
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, size, size);

  context.strokeStyle = "#666";
  context.lineWidth = 2;
  context.beginPath();
  context.arc(center, center, radius, 0, Math.PI * 2);
  context.stroke();

  const path = sequence(1, a, b, n);
  const visibleSegments = traverseActive
    ? traverseStep
    : Math.max(0, path.length - 1);
  const current = traverseActive ? path[Math.min(traverseStep, path.length - 1)] : null;
  for (let index = 1; index <= n; index += 1) {
    const point = pointPosition(index, n, center, radius);
    const highlighted = index === current;
    const pointRadius = highlighted ? 18 : 14;
    context.beginPath();
    context.fillStyle = highlighted ? "yellow" : "white";
    context.strokeStyle = highlighted ? "#b8860b" : "black";
    context.lineWidth = highlighted ? 3 : 1;
    context.arc(point.x, point.y, pointRadius, 0, Math.PI * 2);
    context.fill();
    context.stroke();
    context.fillStyle = "black";
    context.font = `${highlighted ? "bold " : ""}${highlighted ? 10 : 9}px Arial`;
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(String(index), point.x, point.y);
  }

  context.strokeStyle = "blue";
  context.lineWidth = 2;
  for (let index = 0; index < visibleSegments; index += 1) {
    const first = pointPosition(path[index], n, center, radius);
    const second = pointPosition(path[index + 1], n, center, radius);
    context.beginPath();
    context.moveTo(first.x, first.y);
    context.lineTo(second.x, second.y);
    context.stroke();
  }

  if (traverseActive) {
    setPopup(current, pointPosition(current, n, center, radius), size);
  } else {
    popup.hidden = true;
  }
}

function refreshAfterParams() {
  params();
  if (traverseActive) {
    traverseStep = 0;
  }
  render();
}

function setTraverse(active) {
  traverseActive = active;
  traverseStep = 0;
  traverseButton.textContent = active ? "Stop Traverse" : "Traverse";
  nextButton.hidden = !active;
  render();
}

function advance() {
  if (!traverseActive) {
    return;
  }
  const { n, a, b } = params();
  const path = sequence(1, a, b, n);
  if (traverseStep >= path.length - 1) {
    setTraverse(false);
    return;
  }
  traverseStep += 1;
  render();
  if (traverseStep >= path.length - 1) {
    setTraverse(false);
  }
}

function nudge(delta) {
  const upper = maxN();
  const value = Math.min(upper, Math.max(1, Number(nSlider.value) + delta));
  nSlider.value = String(value);
  refreshAfterParams();
}

maxNInput.addEventListener("change", refreshAfterParams);
maxNInput.addEventListener("blur", refreshAfterParams);
nSlider.addEventListener("input", refreshAfterParams);
aInput.addEventListener("change", refreshAfterParams);
aInput.addEventListener("blur", refreshAfterParams);
bInput.addEventListener("change", refreshAfterParams);
bInput.addEventListener("blur", refreshAfterParams);
traverseButton.addEventListener("click", () => setTraverse(!traverseActive));
nextButton.addEventListener("click", advance);
minusButton.addEventListener("click", () => nudge(-1));
plusButton.addEventListener("click", () => nudge(1));
window.addEventListener("resize", render);
window.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    advance();
  } else if (event.key === "PageUp") {
    event.preventDefault();
    nudge(1);
  } else if (event.key === "PageDown") {
    event.preventDefault();
    nudge(-1);
  }
});

if ("serviceWorker" in navigator &&
    (window.isSecureContext || location.hostname === "localhost" || location.hostname === "127.0.0.1")) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

render();
