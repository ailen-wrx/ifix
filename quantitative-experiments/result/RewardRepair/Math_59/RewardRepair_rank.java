return (a < b)? b : (Float.isNaN(a + b)? Float.NaN : a);
return (a >= b)? a : (Float.isNaN(a + b)? Float.NaN : b);
