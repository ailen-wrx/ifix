cluster_1: return getChromosomes().iterator();
cluster_1: chromosomes = getChromosomes();
cluster_1: return Collections.unmodifiableList(chromosomes).iterator();
cluster_1: return Collections.unmodifiableCollection(chromosomes).iterator();
cluster_1: return chromosomes == null ? null : getChromosomes().iterator();
cluster_1: synchronized(chromosomes){
return getChromosomes().iterator();
}
cluster_1: return (Iterator<Chromosome>)getChromosomes().iterator();
