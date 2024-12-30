cluster_1: assert(n.getJSType()!= null && parent.isAssign());
cluster_3: if (n.getJSType()!= null) return;
cluster_4: n.setJSType(n.getJSType());
cluster_2: JSType parentType = getJSType(n.getFirstChild());
cluster_6: try { } catch (Exception e) { return; }
cluster_5: ensureTyped(t, n);
