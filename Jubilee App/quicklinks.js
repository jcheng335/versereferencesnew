// quicklinks.js: shows quick links on the right panel.

////////////////////////////////////////////////////////////////////
// Handle quick links.
function quick_links()
{
  try{
  var bk,basename=main.location.pathname
                  .replace(/^.*[\\\/]/,'').replace(/\.htm$/,'')

  // Index page.
  if(basename=='b')return main_quick_links()
  
  // About page.
  if(basename=='about')return about_quick_links()

  // Books Info page.
  if(basename=='bkinfo')return bkinfo_quick_links()

  // Standard book.
  if((bk=BkAbbrNum[basename.substring(0,3)])!=null)
    return book_quick_links(bk)
  
  // Anything to do with concordance.
  if(basename.substring(0,2)=='cc')
    return cc_quick_links()

  }catch(e){ex("quick_links",e)}
}
function main_quick_links()
{
  try{
  // Set title as indicator of what it is currently showing.
  if(right.document.title=="index")return
  right.document.title="index"

  right.document.body.innerHTML=
    "<br><q><a target=main href=a.htm>Home</a></q>"
    +"<em><a target=_parent href=a.htm>&bull; No Frames</a></em>"
    +"<em><a target=main href=vsearch.htm>&bull; Search</a></em>"
    +"<em><a target=main href=listv.htm>&bull; List Verses</a></em>"
    +"<em><a target=main href=bkinfo.htm>&bull; Books Info</a></em>"
    +"<em><a target=main href=cc.htm>&bull; Concordance</a></em>"
    +"<em><a target=main href=cm.htm>&bull; Charts & Maps</a></em>"
    +"<em><a target=main href=about.htm>[About]</a></em>"
  }catch(e){ex("main_quick_links",e)}
}
function about_quick_links()
{
  try{
  // Set title as indicator of what it is currently showing.
  if(right.document.title=="about")return
  right.document.title="about"

  right.document.body.innerHTML=
    "<br><q><a target=main href=about.htm>About</a></q>"
    +"<em><a target=main href=about.htm#authors>"
    +"&bull; Authors</a></em>"
    +"<em><a target=main href=about.htm#intro>"
    +"&bull; Introduction</a></em>"
    +"<em><a target=main href=about.htm#brief>"
    +"&bull; A Brief Explanation</a></em>"
    +"<em><a target=main href=about.htm#ot>"
    +"&bull; Comments on the OT</a></em>"
    +"<em><a target=main href=about.htm#terms>"
    +"&bull; Terms, Abbreviations, and Conventions</a></em>"
    +"<em><a target=main href=about.htm#bottom>"
    +"&bull; Page Bottom</a></em>"
    +"<em><a target=main href=a.htm>[Home]</a></em>"
  }catch(e){ex("about_quick_links",e)}
}
function bkinfo_quick_links()
{
  try{
  // Set title as indicator of what it is currently showing.
  if(right.document.title=="bkinfo")return
  right.document.title="bkinfo"

  right.document.body.innerHTML=
    "<br><q><a target=main href=bkinfo.htm>Books Info</a></q>"
    +"<em><a target=main href=bkinfo.htm#ot>"
    +"&bull; OT Books Summary</a></em>"
    +"<em><a target=main href=bkinfo.htm#nt>"
    +"&bull; NT Books Summary</a></em>"
    +"<em><a target=main href=bkinfo.htm#ottime>"
    +"&bull; OT Books in Time Order</a></em>"
    +"<em><a target=main href=bkinfo.htm#nttime>"
    +"&bull; NT Books in Time Order</a></em>"
    +"<em><a target=main href=bkinfo.htm#bottom>"
    +"&bull; Page Bottom</a></em>"
    +"<em><a target=main href=a.htm>[Home]</a></em>"
  }catch(e){ex("bkinfo_quick_links",e)}
}
function book_quick_links(bk)
{
  try{
  var s,bkabbr=BkAbbr[bk],i,prevbkabbr,nextbkabbr
  
  // Set title as indicator of what it is currently showing.
  if(right.document.title==bkabbr)return
  right.document.title=bkabbr
  
  // Set quick links for current book.
  prevbkabbr=BkAbbr[bk==0?NumBks-1:bk-1]
  nextbkabbr=BkAbbr[bk==NumBks-1?0:bk+1]
  s="<br><q><a target=main href="+prevbkabbr
   +".htm><img border=0 src=left10x10.png></a> "
   +"<u><a target=main href="+bkabbr+".htm>"+BkRef[bk]+"</a></u>"
   +" <a target=main href="+nextbkabbr
   +".htm><img border=0 src=right10x10.png></a></q>"
   +"<a target=main href="+bkabbr+".htm#intro>Intro</a><br>"
   +"<a target=main href="+bkabbr+".htm#subject>Subject</a><br>"
   +"<a target=main href="+bkabbr+"O.htm>Outline</a><br>"
   +"<a target=main href="+bkabbr+"N.htm>Notes</a><br>"
   +"<br>Chapters"
   
  for(i=1;i<=BkNumChs[bk];i++)
  {
    if(i==1||i%5==0)
      s+="<br><a target=main href="+bkabbr+".htm#v"+i+">"+i+"</a>"
    else
      s+="&nbsp;<a target=main href="+bkabbr+".htm#v"+i+">&bull;</a>"
  }
  s+="<br><br><a target=main href=a.htm>[Home]</a>"

  right.document.body.innerHTML=s
  }catch(e){ex("book_quick_links",e)}
}
function cc_quick_links()
{
  try{
  var s,i,ord_a='a'.charCodeAt(0),ord_z='z'.charCodeAt(0)

  // Set title as indicator of what it is currently showing.
  if(right.document.title=='cc')return
  right.document.title='cc'

  // Quick links for the concordance.
  s="<br><q><a target=main href=cc.htm>Concordance</a></q><em>"
  for(i=ord_a;i<=ord_z;i++)
  {
    var c=String.fromCharCode(i)
    if((i-ord_a)%4)s+=".";else if(i!=ord_a)s+="<br>"
    s+="<a target=main href=cc"+c+".htm> "+c+" </a>"
  }
  s+="</em><em><a target=main href=a.htm>[Home]</a></em>"

  right.document.body.innerHTML=s
  }catch(e){ex("book_quick_links",e)}
}
////////////////////////////////////////////////////////////////////
