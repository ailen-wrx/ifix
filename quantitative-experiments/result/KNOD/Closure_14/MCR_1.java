cluster_1: cfa.createEdge(fromNode,Branch.ON_EX,finallyNode);
cluster_1: cfa.createEdge(fromNode,Branch.UNCOND,node.getFirstChild());
cluster_1: cfa.createEdge(fromNode,Branch.UNCOND,node.getLastChild());
cluster_1: if (mayThrowException(fromNode) ){
return parent;
}
