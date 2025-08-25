// listv.js: list verses

////////////////////////////////////////////////////////////////////
// Recognizing any partial/complete book names.
var BkRX=[],BkAbbrLcNum=[],BkRefLcNum=[],BkRefLcMaxLen=0,digitx=/^\d/

function init_recog_bkname()
{
  try{
  BkRX[0]=/^(Ge?n?e?s?i?s?)($|[^a-zA-Z])/i
  BkRX[1]=/^(Ex?o?d?u?s?)($|[^a-zA-Z])/i
  BkRX[2]=/^(Le?v?i?t?i?c?u?s?)($|[^a-zA-Z])/i
  BkRX[3]=/^(Nu?m?b?e?r?s?)($|[^a-zA-Z])/i
  BkRX[4]=/^(De?u?t?e?r?o?n?o?m?y?)($|[^a-zA-Z])/i
  BkRX[5]=/^(Jo?s?h?u?a?)($|[^a-zA-Z])/i
  BkRX[6]=/^(Ju?d?g?e?s?)($|[^a-zA-Z])/i
  BkRX[7]=/^(Ru?t?h?)($|[^a-zA-Z])/i
  BkRX[8]=/^(((1)|(1st)|(First))[\s\xA0]*Sa?m?u?e?l?)($|[^a-zA-Z])/i
  BkRX[9]=/^(((2)|(2nd)|(Second))[\s\xA0]*Sa?m?u?e?l?)($|[^a-zA-Z])/i
  BkRX[10]=/^(((1)|(1st)|(First))[\s\xA0]*Ki?n?g?s?)($|[^a-zA-Z])/i
  BkRX[11]=/^(((2)|(2nd)|(Second))[\s\xA0]*Ki?n?g?s?)($|[^a-zA-Z])/i
  BkRX[12]=/^(((1)|(1st)|(First))[\s\xA0]*Ch?r?o?n?i?c?l?e?s?)($|[^a-zA-Z])/i
  BkRX[13]=/^(((2)|(2nd)|(Second))[\s\xA0]*Ch?r?o?n?i?c?l?e?s?)($|[^a-zA-Z])/i
  BkRX[14]=/^(Ez?r?a?)($|[^a-zA-Z])/i
  BkRX[15]=/^(Ne?h?e?m?i?a?h?)($|[^a-zA-Z])/i
  BkRX[16]=/^(Es?t?h?e?r?)($|[^a-zA-Z])/i
  BkRX[17]=/^(Jo?b?)($|[^a-zA-Z])/i
  BkRX[18]=/^(Ps?a?l?m?s?)($|[^a-zA-Z])/i
  BkRX[19]=/^(Pr?o?v?e?r?b?s?)($|[^a-zA-Z])/i
  BkRX[20]=/^(Ec?c?l?e?s?i?a?s?t?e?s?)($|[^a-zA-Z])/i
  BkRX[21]=/^((S\.?S($|[^a-zA-Z]))|(Song([\s\xA0]*of[\s\xA0]*((Songs)|(Solomon)))($|[^a-zA-Z])))/i
  BkRX[22]=/^(Is?a?i?a?h?)($|[^a-zA-Z])/i
  BkRX[23]=/^(Je?r?e?m?i?a?h?)($|[^a-zA-Z])/i
  BkRX[24]=/^(La?m?e?n?t?a?t?i?o?n?s?)($|[^a-zA-Z])/i
  BkRX[25]=/^(Ez?e?k?i?e?l?)($|[^a-zA-Z])/i
  BkRX[26]=/^(Da?n?i?e?l?)($|[^a-zA-Z])/i
  BkRX[27]=/^(Ho?s?e?a?)($|[^a-zA-Z])/i
  BkRX[28]=/^(Jo?e?l?)($|[^a-zA-Z])/i
  BkRX[29]=/^(Am?o?s?)($|[^a-zA-Z])/i
  BkRX[30]=/^(Ob?a?d?i?a?h?)($|[^a-zA-Z])/i
  BkRX[31]=/^(Jo?n?a?h?)($|[^a-zA-Z])/i
  BkRX[32]=/^(Mi?c?a?h?)($|[^a-zA-Z])/i
  BkRX[33]=/^(Na?h?u?m?)($|[^a-zA-Z])/i
  BkRX[34]=/^(Ha?b?a?k?k?u?k?)($|[^a-zA-Z])/i
  BkRX[35]=/^(Ze?p?h?a?n?i?a?h?)($|[^a-zA-Z])/i
  BkRX[36]=/^(Ha?g?g?a?i?)($|[^a-zA-Z])/i
  BkRX[37]=/^(Ze?c?h?a?r?i?a?h?)($|[^a-zA-Z])/i
  BkRX[38]=/^(Ma?l?a?c?h?i?)($|[^a-zA-Z])/i
  BkRX[39]=/^(Ma?t?t?h?e?w?)($|[^a-zA-Z])/i
  BkRX[40]=/^(Ma?r?k?)($|[^a-zA-Z])/i
  BkRX[41]=/^(Lu?k?e?)($|[^a-zA-Z])/i
  BkRX[42]=/^(Jo?h?n?)($|[^a-zA-Z])/i
  BkRX[43]=/^(Ac?t?s?)($|[^a-zA-Z])/i
  BkRX[44]=/^(Ro?m?a?n?s?)($|[^a-zA-Z])/i
  BkRX[45]=/^(((1)|(1st)|(First))[\s\xA0]*Co?r?i?n?t?h?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[46]=/^(((2)|(2nd)|(Second))[\s\xA0]*Co?r?i?n?t?h?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[47]=/^(Ga?l?a?t?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[48]=/^(Ep?h?e?s?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[49]=/^(Ph?i?l?i?p?p?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[50]=/^(Co?l?o?s?s?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[51]=/^(((1)|(1st)|(First))[\s\xA0]*Th?e?s?s?a?l?o?n?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[52]=/^(((2)|(2nd)|(Second))[\s\xA0]*Th?e?s?s?a?l?o?n?i?a?n?s?)($|[^a-zA-Z])/i
  BkRX[53]=/^(((1)|(1st)|(First))[\s\xA0]*Ti?m?o?t?h?y?)($|[^a-zA-Z])/i
  BkRX[54]=/^(((2)|(2nd)|(Second))[\s\xA0]*Ti?m?o?t?h?y?)($|[^a-zA-Z])/i
  BkRX[55]=/^(Ti?t?u?s?)($|[^a-zA-Z])/i
  BkRX[56]=/^(Ph?i?l?e?m?o?n?)($|[^a-zA-Z])/i
  BkRX[57]=/^(He?b?r?e?w?s?)($|[^a-zA-Z])/i
  BkRX[58]=/^(Ja?m?e?s?)($|[^a-zA-Z])/i
  BkRX[59]=/^(((1)|(1st)|(First))[\s\xA0]*Pe?t?e?r?)($|[^a-zA-Z])/i
  BkRX[60]=/^(((2)|(2nd)|(Second))[\s\xA0]*Pe?t?e?r?)($|[^a-zA-Z])/i
  BkRX[61]=/^(((1)|(1st)|(First))[\s\xA0]*Jo?h?n?)($|[^a-zA-Z])/i
  BkRX[62]=/^(((2)|(2nd)|(Second))[\s\xA0]*Jo?h?n?)($|[^a-zA-Z])/i
  BkRX[63]=/^(((3)|(3rd)|(Third))[\s\xA0]*Jo?h?n?)($|[^a-zA-Z])/i
  BkRX[64]=/^(Ju?d?e?)($|[^a-zA-Z])/i
  BkRX[65]=/^(Re?v?e?l?a?t?i?o?n?)($|[^a-zA-Z])/i  

  // BkAbbrLcNum.
  var i
  for(i=BkAbbr.length-1;i>=0;i--)
    BkAbbrLcNum[BkAbbr[i].toLowerCase()]=i

  // BkRefLcNum.
  BkRefLcMaxLen=0
  for(i=BkRef.length-1;i>=0;i--)
  {
    var len=BkRef[i].length
    if(len>BkRefLcMaxLen)BkRefLcMaxLen=len
    try{if(!BkRefLcNum[len])BkRefLcNum[len]=[]}
    catch(e){BkRefLcNum[len]=[]}
    BkRefLcNum[len][BkRef[i].toLowerCase()]=i

    if(!/\./.test(BkRef[i]))continue
    var s=BkRef[i].replace(/\./g,"")
    len=s.length
    try{if(!BkRefLcNum[len])BkRefLcNum[len]=[]}
    catch(e){BkRefLcNum[len]=[]}
    BkRefLcNum[len][s.toLowerCase()]=i
  }
  
  }catch(e){ex("init_recog_bkname",e)}
}

// Returns [bkindex, match_string].
function recog_bkname(s)
{
  try{
  if(s.length<2)return null

  var a,i
  
  // Init BkAbbrLcNum.
  if(BkRX.length==0)init_recog_bkname()

  // Try matching by BkAbbr first.
  if(a=/^\w\w\w($|[^a-zA-Z])/.test(s))
  {
    a=s.substring(0,3)
    i=BkAbbrLcNum[a.toLowerCase()]
    if(i!=null)return [i,a]
  }
  
  // Try matching BkRef next.
  for(var len=BkRefLcMaxLen;len>=4;len--)
  {
    if(s.length<len)continue
    try{if(!BkRefLcNum[len])continue}catch(e){continue}
    if(s.length>len && /[a-zA-Z]/.test(s.charAt(len)))continue
    a=s.substring(0,len)
    i=BkRefLcNum[len][a.toLowerCase()]
    if(i!=null)return [i,a]
  }
  
  // Match by regex.
  for(i=BkRX.length-1;i>=0;i--)
    if(a=BkRX[i].exec(s))
    {
      if(digitx.test(a[1]))
        {if(a[1].length>2)return [i,a[1]]}
      else
        {if(a[1].length>1)return [i,a[1]]}
    }
  }catch(e){ex("recog_bkname",e)}
  return null
}
// Returns an array of text vrefs eg. "Gen1:1" for verse refs given.
function parse_vrefs(s)
{
  var a,i,rv=[],bk=0,ch=0,vn,is_chap=1,has_bk=0,has_range=0
  try{
  var t=s
  while(t.length)
  {
    // Any human-readable book name.
    if(a=recog_bkname(t))
    {
      if(has_bk)rv.push(BkAbbr[bk])
      else has_bk=1
      bk=a[0]
      is_chap=1
      t=t.substring(a[1].length)
      continue
    }
    // Whole chapter:verse notations.
    a=/^((\d+)[\s\xA0]*:[\s\xA0]*(\d+)[a-z]?)/.exec(t)
    if(a)
    {
      ch=a[2]
      vn=a[3]
      is_chap=0
      has_bk=0
      rv.push(BkAbbr[bk]+ch+":"+vn)
      t=t.substring(a[1].length)
      continue
    }
    // Single number -- must be verse.
    a=/^((\d+)[a-z])/.exec(t)
    if(a)
    {
      vn=a[2]
      is_chap=0
      has_bk=0
      rv.push(BkAbbr[bk]+ch+":"+vn)
      t=t.substring(a[1].length)
      continue
    }
    // Single number -- could be chapter or verse.
    a=/^(\d+)/.exec(t)
    if(a)
    {
      if(is_chap){ch=a[1];rv.push(BkAbbr[bk]+ch)}
      else {vn=a[1];rv.push(BkAbbr[bk]+ch+":"+vn)}
      has_bk=0
      t=t.substring(a[1].length)
      continue
    }
    // Range.
    if(/^[\-\—]/.test(t))
    {
      has_range=1
      has_bk=0
      rv.push("-")
      t=t.substring(1)
      continue
    }
    // Any junk string. Eat it.
    a=/^([a-zA-Z]+)/.exec(t)
    if(a)
    {
      t=t.substring(a[1].length)
      continue
    }
    // Semi-colon.
    if(t.charAt(0)==';')
    {
      if(has_bk){rv.push(BkAbbr[bk]);has_bk=0}
    }
    // Any other stuff. Eat one character.
    t=t.substring(1)
  }
  if(has_bk)rv.push(BkAbbr[bk])
  
  // Fix up all ranges.
  if(has_range)
  {
    // Remove duplicate ranges.
    for(i=0;i<rv.length-1;i++)
      if(rv[i]=="-"&&rv[i+1]=="-"){rv.splice(i,1);i--}
      
    // Remove leading and trailing ranges.
    while(rv.length&&rv[0]=="-")rv.shift()
    while(rv.length&&rv[rv.length-1]=="-")rv.pop()
    
    // Merge ranges.
    for(i=1;i<rv.length-1;i++)
      if(rv[i]=="-"){rv[i-1]+="-"+rv[i+1];rv.splice(i,2);i--}
  }

  }catch(e){ex("parse_vrefs",e)}
  return rv
}
// Returns a proper vref string given an array.
function getvrefstring(a)
{
  try{
  var bk=-1,ch=0,vn=0,i,j,s="",t,b,c,bk1=-2,ch1,vn1
  for(i=0;i<a.length;i++)
  {
    t=a[i]
    if((j=t.indexOf("-"))!=-1)
    {
      c=t.substring(j+1)
      t=t.substring(0,j)
    }
    
    b=getvrefstring1(bk,ch,vn,t)
    if(s)s+=b[4]+" "
    bk=b[0];ch=b[1];vn=b[2];s+=b[3]
    
    if(j!=-1)
    {
      b=getvrefstring1(bk,ch,vn,c)
      bk=b[0];ch=b[1];vn=b[2];s+="-"+b[3]
    }
  }
  return s
  }catch(e){ex("getvrefstring",e)}
}
// Helper function for getvrefstring().
// Returns [new_bk, new_ch, new_vn, vref_string, appender]
function getvrefstring1(bk,ch,vn,s)
{
  try{
  var b,bk1,ch1,vn1,sep=";"
  if(b=/^(\w\w\w)(\d+):(\d+)$/.exec(s))
  {
    bk1=BkAbbrNum[b[1]]
    ch1=b[2]
    vn1=b[3]
    if(bk!=bk1)s=bkref_vref(bk1,ch1,vn1)
    else if(ch!=ch1)s=(BkNumChs[bk1]==1?"":ch1+":")+vn1
    else {sep=",";s=vn1}
    bk=bk1;ch=ch1;vn=vn1
  }
  else if(b=/^(\w\w\w)(\d+)$/.exec(s))
  {
    bk1=BkAbbrNum[b[1]]
    ch1=b[2]
    if(bk!=bk1)s=BkRef[bk1]+(BkNumChs[bk1]==1?"":" "+ch1)
    else
    {
      if(BkNumChs[bk1]==1)sep=","
      s=(BkNumChs[bk1]==1?BkRef[bk1]:"")+ch1
    }
    bk=bk1;ch=ch1;vn=0
  }
  else if(/^\w\w\w$/.test(s))
  {
    bk=BkAbbrNum[s]
    s=BkName[bk]
    ch=0;vn=0
  }
  else
  {
    s+="["+s+"?]"
  }

  return [bk,ch,vn,s,sep]
  }catch(e){ex("getvrefstring1",e)}
}
var unknown_vref="Unknown verse reference"
function bad_ch(bk,ch)
{
  return BkRef[bk]+" "+ch+"\xA0No such chapter (valid: 1-"+
         BkNumChs[bk]+")"
}
function bad_vn(bk,ch,vn)
{
  if(ch<1||ch>BkNumChs[bk])return bad_ch(bk,ch)
  return BkRef[bk]+" "+(BkNumChs[bk]==1?"":ch+":")+vn+
         "\xA0No such verse (valid: 1-"+BkChNV[bk][ch-1]+")"
}
function bad_vr(s)
{
  return s+"\xA0Unknown verse reference"
}
// Given a vref string, return an array of all vrefs as: [hashkey,errmsg]
function getbyvref(orig_s,limit)
{
  var s=orig_s
  if(limit<0)limit=0
  try{
  // Do range.
  var bk1=0,ch1=1,vn1=1,bk2=0,ch2=1,vn2=1
  var i=s.indexOf("-")
  if(i!=-1)
  {
    // Range.
    var a,t=s.substring(i+1)
    s=s.substring(0,i)
    
    // From vref.
    if(a=/^(\w\w\w)(\d+):(\d+)$/.exec(s))
    {
      bk1=BkAbbrNum[a[1]]
      ch1=int(a[2])
      vn1=int(a[3])
      if(vref_not_ok(bk1,ch1,vn1))return [bad_vn(bk1,ch1,vn1)]
    }
    else if(a=/^(\w\w\w)(\d+)$/.exec(s))
    {
      bk1=BkAbbrNum[a[1]]
      if(BkNumChs[bk1]==1){ch1=1;vn1=int(a[2])}
      else {ch1=int(a[2]);vn1=1}
      if(vref_not_ok(bk1,ch1,vn1))return [bad_ch(bk1,ch1)]
    }
    else if(/^\w\w\w$/.exec(s))
    {
      bk1=BkAbbrNum[s]
      ch1=vn1=1
    }
    else return [bad_vr(s)]

    // To vref.
    if(a=/^(\w\w\w)(\d+):(\d+)$/.exec(t))
    {
      bk2=BkAbbrNum[a[1]]
      ch2=int(a[2])
      vn2=int(a[3])
      if(vref_not_ok(bk2,ch2,vn2))return [bad_vn(bk2,ch2,vn2)]
    }
    else if(a=/^(\w\w\w)(\d+)$/.exec(t))
    {
      bk2=BkAbbrNum[a[1]]
      if(BkNumChs[bk2]==1){ch2=1;vn2=int(a[2])}
      else {ch2=int(a[2]);vn2=BkChNV[bk2][ch2-1]}
      if(vref_not_ok(bk2,ch2,vn2))return [bad_ch(bk2,ch2)]
    }
    else if(/^\w\w\w$/.exec(t))
    {
      bk2=BkAbbrNum[t]
      ch2=BkNumChs[bk2]
      vn2=BkChNV[bk2][ch2-1]
    }
    else return [bad_vr(t)]
  }
  else
  {
    // Single vref.
    if(a=/^(\w\w\w)(\d+):(\d+)$/.exec(s))
    {
      bk1=bk2=BkAbbrNum[a[1]]
      ch1=ch2=int(a[2])
      vn1=vn2=int(a[3])
      if(vref_not_ok(bk1,ch1,vn1))return [bad_vn(bk1,ch1,vn1)]
    }
    else if(a=/^(\w\w\w)(\d+)$/.exec(s))
    {
      bk1=bk2=BkAbbrNum[a[1]]
      if(BkNumChs[bk1]==1){ch1=ch2=1;vn1=vn2=int(a[2])}
      else {ch1=ch2=int(a[2]);vn1=1;vn2=BkChNV[bk1][ch1-1]}
      if(vref_not_ok(bk1,ch1,vn1))return [bad_ch(bk1,ch1)]
    }
    else if(/^\w\w\w$/.exec(s))
    {
      bk1=bk2=BkAbbrNum[s]
      ch1=1;vn1=1
      ch2=BkNumChs[bk2]
      vn2=BkChNV[bk2][ch2-1]
    }
    else return [bad_vr(s)]
  }
  return getbyvref1(bk1,ch1,vn1,bk2,ch2,vn2,limit)
  }catch(e){ex("getbyvref",e)}
  return []
}
// Helper for getbyvref().
function getbyvref1(bk1,ch1,vn1,bk2,ch2,vn2,limit)
{
  var rv=[]
  try{
  // Note that this is the 2nd time we check the vref.
  // In order to make this function callable by the user,
  // we'll just leave the extra checking here.
  if(vref_not_ok(bk1,ch1,vn1))
  {
    rv.push(bad_vn(bk1,ch1,vn1))
    if(bk1==bk2&&ch1==ch2&&vn1==vn2)return rv
  }
  if(vref_not_ok(bk2,ch2,vn2))rv.push(bad_vn(bk2,ch2,vn2))
  if(rv.length)return rv
  
  for(;bk1<=bk2;bk1++,ch1=1)
  {
    var ch3=(bk1==bk2)?ch2:BkNumChs[bk1]
    for(;ch1<=ch3;ch1++,vn1=1)
    {
      var vn3=(bk1==bk2&&ch1==ch2)?vn2:BkChNV[bk1][ch1-1]
      for(;vn1<=vn3;vn1++)
      {
        rv.push(hkey_verse(bk1,ch1,vn1))
        if(limit&&rv.length>=limit)return rv
      }
    }
  }
  }catch(e){ex("getvyvref1",e)}
  return rv
}
function vref_not_ok(bk,ch,vn)
{
  try{
  if(bk<0||bk>=NumBks||ch<1||ch>BkNumChs[bk]||vn<1||vn>BkChNV[bk][ch-1])
    return 1
  }catch(e){ex("vref_not_ok",e);return 1}
  return 0
}
// Set status for listv.
function listv_setstat(s)
{
  try{
  setstat("<b>"+proper_vstr+"</b>&nbsp; ("
          +vref_list.length+" verse"+(vref_list.length==1?"":"s")
          +") - "+timetaken(startmillis)+" sec."
          +(s?" - "+s:""))
  }catch(e){ex("listv_setstat",e)}
}
// Top-level user-called function.
var TO_LIMIT=10
var vstr,parsed_vrefs,proper_vstr,curfromkeypress,curlimit,listv_busy=0,
    vref_list,current_list_index,listv_timeout=null,listv_canceled
// Delay on auto-onkeypress calls.
function listv(fromkeypress)
{
  try{
  if(listv_timeout){clearTimeout(listv_timeout);listv_timeout=null}
  if(fromkeypress)
  {
    listv_timeout=setTimeout("listv0("+fromkeypress+")",500)
  }
  else
    listv0()
  }catch(e){ex("listv",e)}
}
// List all verses given.
function listv0(fromkeypress)
{
  try{
  // Return if still busy.
  if(fromkeypress&&listv_busy)return
  listv_busy=1

  try{
  // Input from typing into bottom panel.
  if(fromkeypress==2)main.document.f.vr.value=document.f.vr.value

  var i=main.document.f.vr.value
  i=main.document.getElementById("listing")
  }catch(e){setTimeout("listv("+(fromkeypress?1:0)+")",10);return}
  
  // Init variables.
  listv_canceled=0
  startmillis=getmillis()
  vstr=""
  curfromkeypress=fromkeypress?1:0
  parsed_vrefs=[]
  proper_vstr=""
  vref_list=[]

  // Display the cancel button.
  main.document.getElementById("cancelbutton").style.visibility="visible"

  // Get and trim string.
  vstr=main.document.f.vr.value
  if(!curfromkeypress)
  {
    vstr=vstr.replace(/^\s+/,'').replace(/\s+$/,'').replace(/\s\s+/,' ')
    main.document.f.vr.value=vstr
  }
  if(vstr.length==0)return listv_restore()
  
  // Get proper verse references.
  if(listv_canceled)return canceled_listv()
  parsed_vrefs=parse_vrefs(vstr)
  proper_vstr=getvrefstring(parsed_vrefs)
  
  // Check current verses.
  if(main.document.getElementById("lastlisted").innerHTML==proper_vstr)
  {
    if(proper_vstr.length==0)setstat("No verses to list")
    listv_busy=0
    return
  }

  // Set status as proper vrefs.
  listv_setstat("Retrieving all verses")

  // Get all vrefs to list.
  vref_list=[]
  var i,s="",b,j,cnt
  for(i=0,cnt=1;i<parsed_vrefs.length;i++)
  {
    b=getbyvref(parsed_vrefs[i],0)
    for(j=0;j<b.length;j++,cnt++)
    {
      // Build all the DHTML tags for inserting these verses.
      if(curfromkeypress)
      {
        if(cnt<=TO_LIMIT)s+="<p id=p"+cnt+"></p>"
        else if(cnt==TO_LIMIT+1)s+="<p id=pmore class=more></p>"
      }
      else
        s+="<p id=p"+cnt+"></p>"
        
      vref_list.push(b[j])
      if(listv_canceled)return canceled_listv()
    }
  }

  // Short-circuit empty listings.
  if(vref_list.length==0)
    setstat("No verses to list for `"+proper_vstr+"'")
  else
    listv_setstat("Loading all verses")

  // Put in all the DHTML filler tags.
  if(listv_canceled)return canceled_listv()
  main.document.getElementById('listing').innerHTML=s

  // List all verses incrementally.
  current_list_index=0
  listv1()
  
  }catch(e){ex("listv",e)}
}
// Wait for all the tags to load.
function listv1()
{
  try{
  if(listv_canceled)return canceled_listv()
  var n=vref_list.length
  if(curfromkeypress&&vref_list.length>TO_LIMIT)n="more"
  var o=main.document.getElementById('p'+n)
  return listv2()
  }catch(e){}
  setTimeout("listv1()",1)
}
// Load next verse in `vref_list'.
function listv2()
{
  try{
  if(listv_canceled)return canceled_listv()
  var i=current_list_index
  if(i>=vref_list.length)return listv4()
  if(curfromkeypress&&i>=TO_LIMIT)
  {
    main.document.getElementById("pmore").innerHTML=
       "<a class=font href=javascript:document.f.submit()>"
      +"[Click here to see all the verses ...]</a>"
    return listv4()
  }
  // May be an error message instead of a hash key for a verse.
  if(vref_list[i].length==4)
    load_js("idx-bd/"+keyhash(vref_list[i])+".js","listv3()")
  else
    listv3()
  }catch(e){ex("listv2",e)}
}
// Display next verse in `vref_list'.
function listv3()
{
  try{
  if(listv_canceled)return canceled_listv()
  var key=vref_list[current_list_index++]
  var i=current_list_index

  if(key.length==4)
  {
    a=keyvref(key)
    main.document.getElementById('p'+i).innerHTML="<s onclick=hi("+i
      +") onmouseover=hi1() onmouseout=ns()>"+getshownum(i)+")</s> "
      +"<b><a href="+a[1]+">"+a[0]+"</a></b>"
      +"<a><b onclick=rm("+i
      +") onmouseover=rm1() onmouseout=ns()> &nbsp;</b></a>"
      +BD[key]
  }
  else
  {
    var j=key.indexOf("\xA0")
    if(j!=-1)a=[key.substring(0,j),key.substring(j+1)]
    else a=[key,"Unknown verse reference"]
    main.document.getElementById('p'+i).innerHTML="<s onclick=hi("+i
      +") onmouseover=hi1() onmouseout=ns()>"+getshownum(i)+")</s> "
      +"<q onclick=rm("+i+") onmouseover=rm1() onmouseout=ns()>"
      +a[0]+" &nbsp;</q>"+a[1]
  }

  setTimeout("listv2()",1)
  }catch(e){ex("listv3",e)}
}
// To call when listv is canceled.
function canceled_listv()
{
  try{
  var s=main.document.getElementById("status").innerHTML
  setstat((s?s+" - ":"")+"Listing canceled")
  listv_restore()
  }catch(e){ex("canceled_listv",e)}
}
// Finalize listing.
function listv4()
{
  try{
  main.document.getElementById("lastlisted").innerHTML=proper_vstr
  listv_setstat("done")
  listv_restore()
  }catch(e){ex("listv4",e)}
}
// Restore the search form to original state.
function listv_restore()
{
  try{
  main.document.getElementById("cancelbutton").style.visibility="hidden"
  if(!curfromkeypress)main.document.f.vr.select()
  listv_busy=0
  }catch(e){ex("listv_restore",e)}
}
////////////////////////////////////////////////////////////////////
resume_js()