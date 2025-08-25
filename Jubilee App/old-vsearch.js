var sstr,results,sarray,sregex,lastpos,curpos,curindex,curwordnum
var startmillis,rcache=[],rcache_sregex=[],cachekey,search_canceled,numoccurs

function wait_id(id,code)
{
  try{if(main.document.getElementById(id)){eval(code);return}}catch(e){}
  setTimeout("wait_id('"+id+"','"+code+"')",1)
}
var vv_page_not_set=1,vv_startmillis=0
function wait_verses(func)
{
  try{
  if(VV)
  {
    if(vv_startmillis)
    {
      debug("Verses took "+timetaken(vv_startmillis)+" sec. to load")
      vv_startmillis=0
    }
    setTimeout(func,1)
    return
  }
  if(vv_page_not_set)
  {
    vv_page_not_set=0
    load_js("verses.js","wait_verses('"+qesc(func)+"')")
    vv_startmillis=getmillis()
    setstat("Please wait while loading all verses ...")
  }
  }catch(e){top.status=e.message}
}
// To pass in search string as GET params.
function vsearch()
{
  try{

  try{
  var i=main.document.f.ss.value
  i=main.document.getElementById("results0")
  }catch(e){setTimeout("vsearch()",10);return}

  // Init all variables.
  sstr=''
  results=[]
  sarray=[]
  sregex=[]
  lastpos=0
  curpos=0
  curindex=0
  curwordnum=0
  startmillis=getmillis()
  search_canceled=0
  cachekey=""
  numoccurs=0

  // Get and trim string.
  sstr=main.document.f.ss.value
  sstr=sstr.replace(/^\s+/,'').replace(/\s+$/,'').replace(/\s\s+/,' ')
  main.document.f.ss.value=sstr
  if(sstr.length==0)
  {
    setstat("Nothing to search for")
    main.document.f.ss.focus()
    return
  }
  
  // Break into array of keywords and regexes for matching them.
  // Only does case-insensitive whole-words matching.
  var i,j,a,t,s=sstr
  var r1=new RegExp('\\"([^\"]+)\\"'),r2=new RegExp("\\'([^\']+)\\'")
  for(;;)
  {
    a=r1.exec(s)
    if(a){t=a[1].replace(/\s/g,"\xA0");s=s.replace(r1,t);continue}
    a=r2.exec(s)
    if(a){t=a[1].replace(/\s/g,"\xA0");s=s.replace(r2,t);continue}
    break
  }
  sarray=s.split(' ')
  for(i=sarray.length-1;i>=0;i--)
    sarray[i]=sarray[i].replace(/\xA0/g," ")

  // Check that these words actually do appear at all.
  var cannot_use_numoccurs=0,seen=[]
  for(i=sarray.length-1;i>=0;i--)
  {
    if(seen[sarray[i]])
    {
      if(i!=sarray.length-1)sarray[i]=sarray[sarray.length-1]
      sarray.pop()
      continue
    }
    seen[sarray[i]]=1
    
    if(sarray[i].indexOf(" ")!=-1)
      {cannot_use_numoccurs=1;continue}
    if(!WF[sarray[i]])
      {show_final_results();return}
  }
  
  // Sort words by their frequencies, in ascending order, rarest word first.
  for(i=sarray.length-1;i>0;i--)
    for(j=i-1;j>=0;j--)
    {
      var f1=WF[sarray[i]],f2=WF[sarray[j]]
      var cmp=(f1==f2)?(sarray[i]<sarray[j]):(f1<f2)
      if(cmp)
      {
        a=sarray[i]
        sarray[i]=sarray[j]
        sarray[j]=a
      }
    }

  if(cannot_use_numoccurs)numoccurs=Number.MAX_VALUE
  else numoccurs=WF[sarray[0]]

  // Check results cache.
  cachekey=sarray.join(" ")
  if(rcache[cachekey])
  {
    results=rcache[cachekey]
    sregex=rcache_sregex[cachekey]
    lastpos=curpos=0
    // Beware that JavaScript shares arrays with assignment.
    show_final_results()
    return
  }
  else
  {
    // Form regexes for highlighting keywords only.
    for(i=0;i<sarray.length;i++)
      sregex.push(new RegExp("(^|[^a-zA-Z</])("+sarray[i]+")($|[^a-zA-Z>])","g"))

    rcache_sregex[cachekey]=sregex
  }

  // Delay load verses to the last minute.
  wait_verses("vsearch1()")
  }catch(e){ex("vsearch",e)}
}
// Show `Cancel' button.
function vsearch1()
{
  try{
  curindex=0
  main.document.getElementById("cancelbutton").style.visibility="visible"
  setTimeout("show_search_status()",1)

  }catch(e){ex("vsearch1",e)}
}
function show_search_status()
{
  show_current_results("show_search_status_1()")
}
function show_search_status_1()
{
  var percent=Math.floor(curpos*100/VV.length)
  setstat("Searching for `<u>"+sstr+"</u>' "
         +(results.length?"(<b>"+results.length+"</b> results) ":"")
         +"("+percent+"%) ... ... ")
  setTimeout("find_words()",1)
}
var w_regex=/[a-zA-Z<>\/]/
function indexOfWord(s,word,i)
{
  for(;;)
  {
    i=s.indexOf(word,i)
    if(i==-1)return i
    var j=i+word.length
    if(i==0||w_regex.test(s.charAt(i-1))){i=j;continue}
    if(j>s.length||w_regex.test(s.charAt(j))){i=j;continue}
    return i
  }
}
function pos_vref(i)
{
  return BkAbbr[codenum(VV.charAt(i))]
    +codenum(VV.charAt(i+1))+":"+codenum(VV.charAt(i+2))
}
function find_words()
{
  if(search_canceled)
  {
    setstat("Search canceled")
    main.document.getElementById("cancelbutton").style.visibility="hidden"
    return
  }
  
  var nextpos=curpos+500
  while(curpos<nextpos)
  {
    // If we've already found everything, return.
    if(results.length==numoccurs){show_final_results();return}
    
    // Find next.
    // Loop to make sure we don't match encoded vrefs also.
    var k=curpos
    for(;;)
    {
      curpos=indexOfWord(VV,sarray[curwordnum],curpos)
      if(curpos==-1){show_final_results();return}
      if(curpos<4||VV[curpos-1]=="\n"||VV[curpos-2]=="\n"||VV[curpos-3]=="\n")
      {
        curpos+=sarray[curwordnum].length
        if(k>=curpos){alert("loop");return}
        k=curpos
        continue
      }
      break
    }
    curpos=VV.lastIndexOf("\n",curpos)+1
    
    // If single word, always accept match.
    if(sarray.length==1)
      {results.push(curpos);curpos=VV.indexOf("\n",curpos)+1;continue}
    
    // Multiple words - move on to next word to match.
    if(curwordnum==0)
      {curwordnum++;lastpos=curpos;continue}
      
    if(curpos!=lastpos)// curpos remains unchanged
      {curwordnum=0;continue}

    if(curwordnum<sarray.length-1){curwordnum++;continue}
    
    results.push(curpos)
    curwordnum=0
    curpos=VV.indexOf("\n",curpos)+1
  }
  
  show_search_status()
}
function format_vt(vt)
{
  return vt.replace(/([^\<])\//g, "$1 / ")
}
// Highlight all the search keywords.
function hilite_words(vt)
{
  var i
  for(i=sregex.length-1;i>=0;i--)
    vt=vt.replace(sregex[i],"$1<u>$2</u>$3")
  return vt
}
function getshownum(i)
{
  var j=i
  if(i>100)
  {
    j=i%10;
    if(j)j=".."+j
    else j=i
  }
  return j
}
function show_current_results(code)
{
  try{
  if(curindex>=results.length){setTimeout(code,1);return}
  
  var z="",obj=main.document.getElementById("results"+curindex)
  if(!obj){setTimeout("show_current_results('"+code+"')",1);return}
  while(curindex<results.length)
  {
    var pos=results[curindex]
    var bk=codenum(VV.charAt(pos++))
    var ch=codenum(VV.charAt(pos++))
    var vn=codenum(VV.charAt(pos++))
    var vt=VV.substring(++pos, VV.indexOf("\n",pos))
    var vr="<b><a href="+BkAbbr[bk]+".htm#v"+ch+"_"+vn+">"
      +BkRef[bk]+' '+(BkNumChs[bk]==1?'':ch+':')+vn+"</a></b>"
    
    curindex++
    z+="<p id=p"+curindex+"><s onclick=hi("+curindex
      +") onmouseover=hi1() onmouseout=ns()>"+getshownum(curindex)+")</s> "
      +vr+"<s onclick=rm("+curindex
      +") onmouseover=rm1() onmouseout=ns()>\xA0\xA0</s>"
      +hilite_words(format_vt(vt))+"</p>"
  }
  obj.innerHTML=z+"<div id=results"+curindex+"></div>"
  wait_id("results"+curindex,code)
  }catch(e){ex("show_current_results",e)}
}
var was_cached
function show_final_results()
{
  try{
  was_cached=rcache[cachekey]?1:0

  // Store current results in cache.
  if(!rcache[cachekey])
  {
    rcache[cachekey]=results

    // Refresh search results to deal with Firefox bug.
    if(!document.all)
    {
      curindex=0
      main.document.getElementById("results0").innerHTML=""
      show_current_results("show_final_results_1()")
      return
    }
  }

  // Flush all remaining results.
  show_current_results("show_final_results_1()")
  
  }catch(e){ex("show_final_results",e)}
}
var show_hide_link_printed=0
function show_final_results_1()
{
  try{
  // Show message.
  var f=(results.length==0
      ?"not found"
      :"found in <b>"+results.length+"</b> verse"
        +(results.length==1?"":"s"))
  setstat("String `<u>"+sstr+"</u>' "+f
    +" - "+timetaken(startmillis)+" sec."+(was_cached?" (cached)":""))

  // Restore search form to after-search condition.
  main.document.getElementById("cancelbutton").style.visibility="hidden"
  main.document.f.ss.select()
  
  // Display all results in the left bar.
  var i,s="<q><a target=main href=vsearch.htm?ss="+escape(sstr)
    +">Search for `<u>"+sstr+"</u>' ("+f+")</a></q>"
  for(i=0;i<results.length;)
  {
    var pos=results[i++]
    var bk=codenum(VV.charAt(pos++))
    var ch=codenum(VV.charAt(pos++))
    var vn=codenum(VV.charAt(pos++))

    s+=getshownum(i)+") <a target=main href="+BkAbbr[bk]+".htm#v"+ch+"_"+vn+">"
      +BkRef[bk]+' '+(BkNumChs[bk]==1?'':ch+':')+vn+"</a><br>"
  }
  left.document.body.innerHTML=s
  
  // Link to show left panel.
  if(results.length&&document.data.leftbar_on.value!='1'
     &&!show_hide_link_printed)
  {
    show_hide_link_printed=1
    debug("<a href=javascript:exec('tgshow(\"leftbar\")')>Show/Hide Search Results Panel</a>")
  }
  
  }catch(e){ex("show_final_results_1",e)}
}


resume_js()