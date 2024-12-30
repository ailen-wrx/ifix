return getChromosomes().iterator();
synchronized(chromosomes){
return getChromosomes().iterator();
}
return chromosomes == null ? null : getChromosomes().iterator();
return Collections.unmodifiableList(chromosomes).iterator();
return Collections.unmodifiableCollection(chromosomes).iterator();
chromosomes = getChromosomes();
return (Iterator<Chromosome>)getChromosomes().iterator();
