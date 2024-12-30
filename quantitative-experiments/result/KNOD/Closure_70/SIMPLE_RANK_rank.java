defineSlot(astParameter,functionNode,jsDocParameter.getJSType(),false);
defineSlot(astParameter,jsDocParameters,jsDocParameter.getJSType(),false);
defineSlot(astParameter,astParameters,jsDocParameter.getJSType(),false);
defineSlot(astParameter,functionNode,jsDocParameter.getJSType(),functionType.isConstructor());
defineSlot(astParameter,functionNode,jsDocParameter.getJSType(),functionType.isInterface());
defineSlot(astParameter,functionNode,jsDocParameter.getJSType(),functionType.isInstanceType());
