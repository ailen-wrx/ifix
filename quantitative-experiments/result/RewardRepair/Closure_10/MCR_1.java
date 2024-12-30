cluster_1: return anyResultsMatch(n, MAY_BE_STRING_PREDICATE);
cluster_1: return mayBeStringHelper(n);
cluster_1: recurse = true; return mayBeStringHelper(n);
cluster_1: recurse = false; return mayBeStringHelper(n);
cluster_1: if (recurse) { return mayBeStringHelper(n); } return recurse;
cluster_1: if (recurse) { return mayBeStringHelper(n); } return false;
cluster_1: if (recurse) { return mayBeStringHelper(n); } return true;
cluster_1: if (recurse) { return mayBeStringHelper(n); } return mayBeStringHelper(n);
