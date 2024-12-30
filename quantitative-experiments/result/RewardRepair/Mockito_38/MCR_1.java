cluster_7: return StringDescription.toString(m).equals(String.valueOf(arg));
cluster_6: return arg!= null && StringDescription.toString(m).equals(arg.toString());
cluster_2: return StringDescription.toString(m).equals(arg == null? false : arg.toString());
cluster_3: return StringDescription.toString(m).equals(arg!= null? arg.toString() : null);
cluster_4: if (arg == null) return false; return StringDescription.toString(m).equals(arg.toString());
cluster_5: if (arg!=null) return StringDescription.toString(m).equals(arg.toString()); return false;
cluster_1: try { return StringDescription.toString(m).equals(arg.toString()); } catch (Exception e) { return false; }
