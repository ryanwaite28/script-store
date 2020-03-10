const getgcd = (a, b) => {
  // gets greatest common divisor via Euclidean algorithm.
  // https://en.wikipedia.org/wiki/Euclidean_algorithm
  if (b == 0) {
    return a;
  }
  const aPrime = a % b;
  return getgcd(b, aPrime);
};
