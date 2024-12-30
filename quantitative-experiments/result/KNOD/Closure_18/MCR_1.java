cluster_2: options.dependencyOptions.needsManagement() || options.closurePass
cluster_3: options.dependencyOptions.needsManagement() && options.dependencyOptions.needsManagement()
cluster_1: options.dependencyOptions.needsManagement() && (hasRegExpGlobalReferences() || options.closurePass)
