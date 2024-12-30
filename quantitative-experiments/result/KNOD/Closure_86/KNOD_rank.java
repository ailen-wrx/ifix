return false;
return isObjectLitKey(value,value);
return isLhs(value,value);
return isTryFinallyNode(value,value);
return locals.apply(value);
return REGEXP_METHODS.equals(value.getParent().getNext());
return BUILTIN_FUNCTIONS_WITHOUT_SIDEEFFECTS.equals(value.getParent().getNext());
return CONSTRUCTORS_WITHOUT_SIDE_EFFECTS.equals(value.getParent().getNext());
return OBJECT_METHODS_WITHOUT_SIDEEFFECTS.equals(value.getParent().getNext());
return JSC_PROPERTY_NAME_FN.equals(value.getParent().getNext());
return STRING_REGEXP_METHODS.equals(value.getParent().getNext());
return isFunction(value);
return isName(value);
return mayHaveSideEffects(value);
return isFunctionDeclaration(value);
return isGet(value);
return isGetProp(value);
return isExpressionNode(value);
return isFunctionExpression(value);
return isAssign(value);
return isVar(value);
return isObjectLitKey(value.getParent(),value.getParent());
return isLhs(value.getParent(),value.getParent());
return REGEXP_METHODS.isEmpty();
return BUILTIN_FUNCTIONS_WITHOUT_SIDEEFFECTS.isEmpty();
return CONSTRUCTORS_WITHOUT_SIDE_EFFECTS.isEmpty();
return OBJECT_METHODS_WITHOUT_SIDEEFFECTS.isEmpty();
return JSC_PROPERTY_NAME_FN.isEmpty();
return STRING_REGEXP_METHODS.isEmpty();
return isNameReferenced(value.getParent(),JSC_PROPERTY_NAME_FN);
return has(value,locals,locals);
return locals.apply(value.getParent());
return isObjectLitKey(value,value.getParent());
return isLhs(value,value.getParent());
return locals.apply(value.getLastChild());
return isFunction(value.getParent());
return isName(value.getParent());
return mayHaveSideEffects(value.getParent());
return isFunctionDeclaration(value.getParent());
return isGet(value.getParent());
return isGetProp(value.getParent());
return isExpressionNode(value.getParent());
return isFunctionExpression(value.getParent());
return isAssign(value.getParent());
return isVar(value.getParent());
if (!isFunction(value) ){
return false;
}
if (!isName(value) ){
return false;
}
if (!mayHaveSideEffects(value) ){
return false;
}
if (!isFunctionDeclaration(value) ){
return false;
}
if (!isGet(value) ){
return false;
}
if (!isGetProp(value) ){
return false;
}
if (!isExpressionNode(value) ){
return false;
}
if (!isFunctionExpression(value) ){
return false;
}
if (!isAssign(value) ){
return false;
}
if (!isVar(value) ){
return false;
}
if (value.isEquivalentTo(value) ){
return false;
}
if (value.checkTreeEqualsSilent(value) ){
return false;
}
if (value.checkTreeTypeAwareEqualsSilent(value) ){
return false;
}
if (mayHaveSideEffects(value) ){
return false;
}
return locals.apply(value.getFirstChild());
if (!value.hasChild(value) ){
return false;
}
return ControlFlowGraph.isEnteringNewCfgNode(value);
if (Token.printTrees ){
return locals.apply(value);
}
return REGEXP_METHODS.equals(value.getParent());
return BUILTIN_FUNCTIONS_WITHOUT_SIDEEFFECTS.equals(value.getParent());
return CONSTRUCTORS_WITHOUT_SIDE_EFFECTS.equals(value.getParent());
return OBJECT_METHODS_WITHOUT_SIDEEFFECTS.equals(value.getParent());
return JSC_PROPERTY_NAME_FN.equals(value.getParent());
return STRING_REGEXP_METHODS.equals(value.getParent());
return value.getType() == 0;
if (value.hasChildren() ){
return locals.apply(value);
}
if (value.hasOneChild() ){
return locals.apply(value);
}
if (value.hasSideEffects() ){
return locals.apply(value);
}
if (value != null ){
return false;
}
return value.getFirstChild() == locals;
