return (Double.isNaN(x) &&!Double.isNaN(y)) || x == y;
if (Double.isNaN(x) && Double.isNaN(y)) return x == y; else return x == y;
return x == y && (Double.isNaN(x) && Double.isNaN(y)) || x == y;
if (Double.isNaN(x) && Double.isNaN(y)) return false; else return x == y;
return (Double.isInfinite(x) && Double.isNaN(y)) || x == y;
if (Double.isNaN(x) && Double.isNaN(y)) return false; return x == y;
