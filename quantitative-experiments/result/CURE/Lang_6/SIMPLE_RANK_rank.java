1: pos += Character.charCount( Character.codePointAt( input ,0) ) ;
1: pos += Character.charCount( Character.codePointAt( input , pt ) ) ;
2: pos += Character.charCount( Character.codePointAt( input , pos - pos ) ) ;
2: pos += Character.charCount( Character.codePointAt( input , pos &1) ) ;
2: pos += Character.charCount( Character.codePointAt( input , pos /2) ) ;
2: pos += Character.charCount( Character.codePointAt( input , pos /3) ) ;
2: pos += Character.charCount( Character.codePointAt( input ,0) ) ; ;
