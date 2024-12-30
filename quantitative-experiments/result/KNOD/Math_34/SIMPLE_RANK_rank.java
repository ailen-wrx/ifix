return getChromosomes().iterator();
chromosomes = getChromosomes();
return Collections.unmodifiableList(chromosomes).iterator();
return Collections.unmodifiableCollection(chromosomes).iterator();
return chromosomes == null ? null : getChromosomes().iterator();
synchronized(chromosomes){
return getChromosomes().iterator();
}
return (Iterator<Chromosome>)getChromosomes().iterator();
