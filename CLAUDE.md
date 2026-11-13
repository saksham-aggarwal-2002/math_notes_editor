# Project philosophy

- **No junk or legacy code.** No migration shims, fallbacks for old formats, deprecated aliases,
  dead branches or commented-out code. When something changes shape, change it everywhere and
  delete the old way. If an existing install needs fixing, tell the user what to do by hand
  (e.g. re-pick the data folder) instead of carrying code for it.
- Keep it simple and small: the simplest design that works, readable top to bottom.
