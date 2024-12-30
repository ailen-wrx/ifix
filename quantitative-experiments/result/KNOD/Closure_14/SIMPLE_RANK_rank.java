cfa.createEdge(fromNode,Branch.ON_EX,finallyNode);
cfa.createEdge(fromNode,Branch.UNCOND,node.getFirstChild());
cfa.createEdge(fromNode,Branch.UNCOND,node.getLastChild());
if (mayThrowException(fromNode) ){
return parent;
}
