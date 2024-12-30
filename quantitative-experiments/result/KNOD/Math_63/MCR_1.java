cluster_3: return !Double.isNaN(x) && Double.isNaN(y) || x == y;
cluster_4: return Double.isNaN(x) && y == y || x == y;
cluster_2: return x == x && Double.isNaN(y) || x == y;
cluster_1: return Double.isNaN(x) && equals(y,x,x) || x == y;
cluster_5: return !Double.isNaN(x) && x == y;
