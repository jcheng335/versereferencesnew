// goverse.js: jump to any verse based on text input.

////////////////////////////////////////////////////////////////////
var gv_lastbk=0,gv_lastch=1,gv_lastvn=1
function goverse(s)
{
  try{
  var t=s,known=0
  // Any human-readable book name.
  var a=recog_bkname(t)
  if(a)
  {
    gv_lastbk=a[0]
    gv_lastch=0
    gv_lastvn=0
    t=t.substring(a[1].length)
    known=1
  }
  if(a=/^[\s\xA0\.a-zA-Z]*(\d+)[\s\xA0]*:[\s\xA0]*(\d+)/.exec(t))
  {
    gv_lastch=int(a[1])
    gv_lastvn=int(a[2])
    known=1
  }
  else if(a=/^[\s\xA0\.a-zA-Z]*(\d+)/.exec(t))
  {
    if(gv_lastch==0)gv_lastch=int(a[1])
    else gv_lastvn=int(a[1])
    known=1
  }
  if(gv_lastbk<0||gv_lastbk>=NumBks)
    known=0
  else if(gv_lastch==0&&gv_lastvn!=0)
    known=0
  else
  {
    if(gv_lastch>BkNumChs[gv_lastbk])known=0
    else if(gv_lastvn>BkChNV[gv_lastbk][gv_lastch-1])known=0
  }
  if(!known)return alert(unknown_vref(s).replace("\xA0"," - "))
  
  t=BkAbbr[gv_lastbk]+".htm"
  s=BkRef[gv_lastbk]
  
  if(gv_lastch!=0&&gv_lastvn==0)
  {
    t+="#v"+gv_lastch
    s+=" "+gv_lastch
  }
  else if(gv_lastch!=0&&gv_lastch!=0)
  {
    t+="#v"+gv_lastch+"_"+gv_lastvn
    s+=" "+gv_lastch+":"+gv_lastvn
  }

  main.location.href=t
  top.status="Go Verse: "+s
  document.f.gv.select()
  }catch(e){ex("goverse",e)}
}
////////////////////////////////////////////////////////////////////
resume_js()