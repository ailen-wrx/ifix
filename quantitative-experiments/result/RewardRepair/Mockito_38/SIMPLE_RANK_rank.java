return StringDescription.toString(m).equals(String.valueOf(arg));
return arg!= null && StringDescription.toString(m).equals(arg.toString());
return StringDescription.toString(m).equals(arg == null? false : arg.toString());
return StringDescription.toString(m).equals(arg == null? true : arg.toString());
return StringDescription.toString(m).equals(arg==null?true:arg.toString());
return StringDescription.toString(m).equals(arg!= null? arg.toString() : null);
return StringDescription.toString(m).equals(arg!= null? arg.toString() : false);
if (arg == null) return false; return StringDescription.toString(m).equals(arg.toString());
if (arg!=null) return StringDescription.toString(m).equals(arg.toString()); return false;
if(arg!= null) return StringDescription.toString(m).equals(arg.toString()); return false;
if (arg==null) return false; return StringDescription.toString(m).equals(arg.toString());
if(arg == null) return false; return StringDescription.toString(m).equals(arg.toString());
if(arg!=null) return StringDescription.toString(m).equals(arg.toString()); return false;
if (arg!= null) return StringDescription.toString(m).equals(arg.toString()); else return false;
if (arg!=null) return StringDescription.toString(m).equals(arg.toString()); else return false;
if(arg!= null) return StringDescription.toString(m).equals(arg.toString()); else return false;
if(arg!=null) return StringDescription.toString(m).equals(arg.toString()); else return false;
if (arg == null) { return false; } return StringDescription.toString(m).equals(arg.toString());
try { return StringDescription.toString(m).equals(arg.toString()); } catch (Exception e) { return false; }
try { return StringDescription.toString(m).equals(arg.toString()); } catch (Exception t) { return false; }
