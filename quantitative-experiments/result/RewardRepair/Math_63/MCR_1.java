cluster_1: return (Double.isNaN(x) &&!Double.isNaN(y)) || x == y;
cluster_1: return (Double.isInfinite(x) && Double.isNaN(y)) || x == y;
cluster_1: return x == y && (Double.isNaN(x) && Double.isNaN(y)) || x == y;
cluster_1: if (Double.isNaN(x) && Double.isNaN(y)) return false; return x == y;
cluster_1: if (Double.isNaN(x) && Double.isNaN(y)) return false; else return x == y;
cluster_1: if (Double.isNaN(x) && Double.isNaN(y)) return x == y; else return x == y;
