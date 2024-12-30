cluster_1: if (name.inExterns ){
continue  ;
}
cluster_1: if (!name.canCollapse() ){
continue  ;
}
cluster_1: if (namespace.hasExternsRoot() ){
continue  ;
}
cluster_1: if (collapsePropertiesOnExternTypes ){
continue  ;
}
