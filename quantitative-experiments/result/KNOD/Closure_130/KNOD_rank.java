if (!name.canCollapse() ){
continue  ;
}
if (name.inExterns ){
continue  ;
}
if (namespace.hasExternsRoot() ){
continue  ;
}
if (collapsePropertiesOnExternTypes ){
continue  ;
}
