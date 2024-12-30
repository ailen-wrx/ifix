cluster_5: return getPct(( Comparable < ? > ) v ) ;
cluster_6: return v == null ? null : getPct(( Comparable < ? > ) v ) ;
cluster_4: synchronized( v ) { return getPct(( Comparable < ? > ) v ) ; }
cluster_3: return getCumPct( v ) /2.0;
cluster_2: if( v == null ) return 0; return getPct(( Comparable < ? > ) v ) ;
cluster_1: if( v != null ) return getPct(( Comparable ) v ) ; else return 0;
