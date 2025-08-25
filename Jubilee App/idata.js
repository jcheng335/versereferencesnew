// idata.js: access to index data.

////////////////////////////////////////////////////////////////////
// Global index data variables.
var KW=[],BD=[]
////////////////////////////////////////////////////////////////////
// Encoded integers.
function numchar(i){return String.fromCharCode(i+40)}
function charnum(c){return c.charCodeAt(0)-40}
function codenum(i){return i-40}
////////////////////////////////////////////////////////////////////
// Make hash keys.
function hkey_intro(bk)
  {return numchar(bk)+numchar(0)+numchar(1);}
function hkey_subject(bk)
  {return numchar(bk)+numchar(0)+numchar(2);}
function hkey_outline(bk,ch,vn,no,label)
  {return numchar(bk)+numchar(ch)+numchar(vn)+numchar(no)+label;}
function hkey_insert(bk,ch,vn,no)
  {return numchar(bk)+numchar(ch)+numchar(vn)+numchar(50+no);}
function hkey_verse(bk,ch,vn)
  {return numchar(bk)+numchar(ch)+numchar(vn)+numchar(100);}
function hkey_starnote(bk,ch,vn,no)
  {return numchar(bk)+numchar(ch)+numchar(vn)+numchar(100+no);}
function hkey_footnote(bk,ch,vn,no)
  {return numchar(bk)+numchar(ch)+numchar(vn)+numchar(110+no);}
////////////////////////////////////////////////////////////////////
// Recognizing type of stuff.
var key_bk,key_ch,key_vn,key_no
var K_UNKNOWN=0,K_INTRO=1,K_SUBJECT=2,K_FOOTNOTE=3,K_STARNOTE=4,K_VERSE=5,
    K_INSERT=6,K_TITLE=7,K_OUTLINE=8
function key_type(key)
{
  key_bk=codenum(key.charCodeAt(0))
  key_ch=codenum(key.charCodeAt(1))

  if(key.length==3)
  {
    var i=codenum(key.charCodeAt(2))
    if(i==1)return K_INTRO
    if(i==2)return K_SUBJECT
  }
  else if(key.length==4)
  {
    key_vn=codenum(key.charCodeAt(2))
    var i=codenum(key.charCodeAt(3))
    if(i>110){key_no=i-110;return K_FOOTNOTE}
    if(i>100){key_no=i-100;return K_STARNOTE}
    if(i==100)return K_VERSE
    if(i>50){key_no=i-50;return K_INSERT}
    if(i==50)return K_TITLE
  }
  else if(key.length>4)
  {
    key_vn=codenum(key.charCodeAt(2))
    var i=codenum(key.charCodeAt(3))
    if(i>=1&&i<50){key_no=i;return K_OUTLINE}
  }
  return K_UNKNOWN
}
////////////////////////////////////////////////////////////////////
// Returns [bkref_vref, href] for a given key.
function keyvref(key)
{
  var ty=key_type(key)
  if(ty==K_UNKNOWN)return ['[Key '+key+'?]','']

  if(key_vn==0)key_vn='Title'

  switch(ty)
  {
    case K_INTRO:
      return [BkRef[key_bk]+' intro.',BkAbbr[key_bk]+'.htm#intro']
    case K_SUBJECT:
      return [BkRef[key_bk]+' subject',BkAbbr[key_bk]+'.htm#subject']
    case K_FOOTNOTE:
      return [bkref_vref(key_bk,key_ch,key_vn)+'<sup>'+key_no+'</sup>',
              BkAbbr[key_bk]+'N.htm#n'+key_ch+'_'+key_vn+'x'+key_no]
    case K_STARNOTE:
      var stars='******'.substring(0,key_no)
      var SS='SSSSSS'.substring(0,key_no)
      return [bkref_vref(key_bk,key_ch,key_vn)+'<sup>'+stars+'</sup>',
              BkAbbr[key_bk]+'N.htm#n'+key_ch+'_'+key_vn+'x'+SS]
    case K_VERSE:
      return [bkref_vref(key_bk,key_ch,key_vn),
              BkAbbr[key_bk]+'.htm#v'+key_ch+'_'+key_vn]
    case K_INSERT:
      return [bkref_vref(key_bk,key_ch,key_vn)+' header',
              BkAbbr[key_bk]+'.htm#v'+key_ch+'_'+key_vn]
    case K_TITLE:
      return [bkref_vref(key_bk,key_ch,'Title'),
              BkAbbr[key_bk]+'.htm#v'+key_ch+'_Title']
    case K_OUTLINE:
      // Jump target of outline stored after 4th character in key.
      return [bkref_vref(key_bk,key_ch,key_vn)+' outline',
              BkAbbr[key_bk]+'O.htm#'+key.substring(4)]
  }
}
////////////////////////////////////////////////////////////////////
// Hashing algorithm for Bible Data keys.
var BD_NUM_GROUPS=1000
function keyhash(s)
{
  var i=0,h=11
  while(i<s.length)h=h*3+s.charCodeAt(i++)*13+163
  return h%BD_NUM_GROUPS
}
////////////////////////////////////////////////////////////////////
// Loads the data for `key' and calls func when done.
function load_key(key,func)
{
  try{
  load_js("idx-bd/"+keyhash(key)+".js",func)
  }catch(e){ex("load_key",e)}
}
////////////////////////////////////////////////////////////////////
// Gets an encoded word by capitalization.
// `word' must be in lowercase.
function ww_get_word(word,code)
{
  if(code==0) return word
  if(code==2) return word.toUpperCase()
  if(code==1)
  {
    if(word.length==0)return word
    if(word.length==1)return word.toUpperCase()
    return word.charAt(0).toUpperCase()+word.substring(1)
  }
  return code
}
////////////////////////////////////////////////////////////////////
// Checks whether such keyword exists or not.
function ww_get_words(word,match_case,whole_word)
{
  try{
  var rv=[],a,i,s,ic=!match_case,lc=word.toLowerCase()
  // Whole-words-only.
  if(whole_word)
  {
    if(a=WW[lc])
    {
      for(i=1;i<a.length;i++)
      {
        s=ww_get_word(lc,a[i])
        if(ic||word==s)rv.push(s)
      }
    }
  }
  // Partial-words-match.
  else
  {
    // Check all words, could be slow.
    var len=lc.length
    for(var key in WW)
    {
      if(key.length>=len&&key.indexOf(lc)!=-1)
      {
        for(a=WW[key],i=1;i<a.length;i++)
        {
          s=ww_get_word(key,a[i])
          if(ic||s.indexOf(word)!=-1)rv.push(s)
        }
      }
    }
  }
  return rv
  }catch(e){ex("ww_get_words",e)}
}
////////////////////////////////////////////////////////////////////
// Identifies a verse in the fastest way.
function key_is_verse(key)
{
  return key.length==4 && codenum(key.charCodeAt(3))==100
}
// Identifies a footnote in the fastest way.
function key_is_footnote(key)
{
  return key.length==4 && codenum(key.charCodeAt(3))>100
}
