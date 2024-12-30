return anyResultsMatch(n, MAY_BE_STRING_PREDICATE);
return mayBeStringHelper(n);
recurse = true; return mayBeStringHelper(n);
recurse = false; return mayBeStringHelper(n);
if (recurse) { return mayBeStringHelper(n); } return recurse;
if (recurse) { return mayBeStringHelper(n); } return false;
if (recurse) { return mayBeStringHelper(n); } return true;
if (recurse) { return mayBeStringHelper(n); } return mayBeStringHelper(n);
