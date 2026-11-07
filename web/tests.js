import { sequence, wrapValue } from "./game.js";

const results = document.querySelector("#results");
const summary = document.querySelector("#summary");
let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function test(name, callback) {
  const item = document.createElement("li");
  try {
    callback();
    passed += 1;
    item.className = "pass";
    item.textContent = `PASS: ${name}`;
  } catch (error) {
    failed += 1;
    item.className = "fail";
    item.textContent = `FAIL: ${name} — ${error.message}`;
  }
  results.append(item);
}

test("wrapValue handles ordinary and negative values", () => {
  assert(wrapValue(1, 5) === 1, "1 should remain 1");
  assert(wrapValue(6, 5) === 1, "6 should wrap to 1");
  assert(wrapValue(0, 5) === 5, "0 should wrap to 5");
  assert(wrapValue(-1, 5) === 4, "-1 should wrap to 4");
  assert(wrapValue(-7, 5) === 3, "-7 should wrap to 3");
});

test("sequence starts at start and exits on return", () => {
  const values = sequence(1, 2, 1, 6);
  assert(JSON.stringify(values) === JSON.stringify([1, 3, 1]), "known cycle should be [1, 3, 1]");
});

test("sequence respects maxSteps without an early return", () => {
  const values = sequence(1, 1, 1, 7, 3);
  assert(JSON.stringify(values) === JSON.stringify([1, 2, 3, 4]), "maxSteps should cap iterations");
});

test("negative coefficients follow Python modulo semantics", () => {
  const values = sequence(1, -2, -1, 5, 4);
  assert(JSON.stringify(values) === JSON.stringify([1, 2, 5, 4, 1]), "negative path should wrap correctly");
});

summary.textContent = `${passed} passed, ${failed} failed`;
summary.className = failed ? "fail" : "pass";
console.log(`${passed} passed, ${failed} failed`);
