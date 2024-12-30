1: pos += Character.charCount( Character.codePointAt( input , pt ) ) ;
2: pos += Character.charCount( Character.codePointAt( input ,0) ) ;
3: pos += Character.charCount( Character.codePointAt( input ,0) ) ; ;
4: pos += Character.charCount( Character.codePointAt( input , pos - pos ) ) ;
4: pos += Character.charCount( Character.codePointAt( input , pos &1) ) ;
4: pos += Character.charCount( Character.codePointAt( input , pos /2) ) ;
4: pos += Character.charCount( Character.codePointAt( input , pos /3) ) ;
