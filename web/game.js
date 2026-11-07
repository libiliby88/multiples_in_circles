export function wrapValue(value, n) {
  return (((value - 1) % n) + n) % n + 1;
}

export function sequence(start, a, b, n, maxSteps = n) {
  const values = [start];
  let current = start;
  for (let step = 0; step < maxSteps; step += 1) {
    current = wrapValue(a * current + b, n);
    values.push(current);
    if (current === start) {
      break;
    }
  }
  return values;
}
