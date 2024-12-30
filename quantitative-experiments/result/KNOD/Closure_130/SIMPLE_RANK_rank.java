if (name.inExterns ){
continue  ;
}
if (!name.canCollapse() ){
continue  ;
}
if (namespace.hasExternsRoot() ){
continue  ;
}
if (collapsePropertiesOnExternTypes ){
continue  ;
}
