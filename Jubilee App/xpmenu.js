// xpmenu.js: requires `std.js'.

////////////////////////////////////////////////////////////////////
// Input data: 2-D array of menu items.
// Use `--' for hrefs, `==' for javascript code.
var GoItems1=['View',['Switch to Short Menu==tgxpmenu()','','Home Page--a.htm','Blank Page--blank.htm','',"No Frames==location.href=main.location.href",'Show All Panels==show_all_panels()','Hide All Panels (Esc)==hide_all_panels()','Toggle All Superscripts (T)==tg_all_sups()','','Search (S)--vsearch.htm','List Verses (L)--listv.htm','Books Information--bkinfo.htm','Concordance--cc.htm','Charts & Maps--cm.htm','','About--about.htm']]

var GoItems2=['View',['Switch to Long Menu==tgxpmenu()','',"No Frames==location.href=main.location.href",'Show All Panels==show_all_panels()','Hide All Panels (Esc)==hide_all_panels()','Toggle All Superscripts (T)==tg_all_sups()','','Search (S)--vsearch.htm','List Verses (L)--listv.htm','Books Information--bkinfo.htm','Concordance--cc.htm','Charts & Maps--cm.htm','','About--about.htm']]

var xpmenu_items=[]

var xpmenu_items1=[GoItems1,
['Moses',['Genesis--Gen.htm','Exodus--Exo.htm','Leviticus--Lev.htm','Numbers--Num.htm','Deuteronomy--Deu.htm']],
['Israel',['Joshua--Jos.htm','Judges--Jdg.htm','Ruth--Rut.htm','1 Samuel--1Sa.htm','2 Samuel--2Sa.htm','1 Kings--1Ki.htm','2 Kings--2Ki.htm','1 Chronicles--1Ch.htm','2 Chronicles--2Ch.htm','Ezra--Ezr.htm','Nehemiah--Neh.htm','Esther--Est.htm']],
['Poetry',['Job--Job.htm','Psalms--Psa.htm','Proverbs--Prv.htm','Ecclesiastes--Ecc.htm','Song of Songs--SoS.htm']],
['Prophets',['Isaiah--Isa.htm','Jeremiah--Jer.htm','Lamentations--Lam.htm','Ezekiel--Ezk.htm','Daniel--Dan.htm','','Hosea--Hos.htm',
'Joel--Joe.htm','Amos--Amo.htm','Obadiah--Oba.htm','Jonah--Jon.htm','Micah--Mic.htm','Nahum--Nah.htm','Zephaniah--Zep.htm','Haggai--Hag.htm','Zechariah--Zec.htm','Malachi--Mal.htm']],
['Gospels',['Matthew--Mat.htm','Mark--Mrk.htm','Luke--Luk.htm','John--Joh.htm']],
['Paul',['Acts--Act.htm','Romans--Rom.htm','1 Corinthians--1Co.htm','2 Corinthians--2Co.htm','Galatians--Gal.htm','Ephesians--Eph.htm','Philippians--Phi.htm','Colossians--Col.htm','1 Thessalonians--1Th.htm','2 Thessalonians--2Th.htm','1 Timothy--1Ti.htm','2 Timothy--2Ti.htm','Titus--Tit.htm','Philemon--Phm.htm']],
['Others',['Hebrews--Heb.htm','James--Jam.htm','1 Peter--1Pe.htm','2 Peter--2Pe.htm','1 John--1Jo.htm','2 John--2Jo.htm','3 John--3Jo.htm','Jude--Jud.htm','Revelation--Rev.htm']]
]

var xpmenu_items2=[GoItems2,
['Books',['<a class=black href=javascript:go("Gen.htm")>Gen</a> <a class=black href=javascript:go("Exo.htm")>Exo</a> <a class=black href=javascript:go("Lev.htm")>Lev</a> <a class=black href=javascript:go("Num.htm")>Num</a> <a class=black href=javascript:go("Deu.htm")>Deu</a>;',
'<a class=black href=javascript:go("Jos.htm")>Jos</a> <a class=black href=javascript:go("Jdg.htm")>Jdg</a> <a class=black href=javascript:go("Rut.htm")>Rut</a> <a class=black href=javascript:go("1Sa.htm")>1Sa</a> <a class=black href=javascript:go("2Sa.htm")>2Sa</a> <a class=black href=javascript:go("1Ki.htm")>1Ki</a><br><a class=black href=javascript:go("2Ki.htm")>2Ki</a> <a class=black href=javascript:go("1Ch.htm")>1Ch</a> <a class=black href=javascript:go("2Ch.htm")>2Ch</a> <a class=black href=javascript:go("Ezr.htm")>Ezr</a> <a class=black href=javascript:go("Neh.htm")>Neh</a> <a class=black href=javascript:go("Est.htm")>Est</a>;',
'<a class=black href=javascript:go("Job.htm")>Job</a> <a class=black href=javascript:go("Psa.htm")>Psa</a> <a class=black href=javascript:go("Prv.htm")>Prv</a> <a class=black href=javascript:go("Ecc.htm")>Ecc</a> <a class=black href=javascript:go("SoS.htm")>SoS</a>;',
'<a class=black href=javascript:go("Isa.htm")>Isa</a> <a class=black href=javascript:go("Jer.htm")>Jer</a> <a class=black href=javascript:go("Lam.htm")>Lam</a> <a class=black href=javascript:go("Ezk.htm")>Ezk</a> <a class=black href=javascript:go("Dan.htm")>Dan</a>;',
'<a class=black href=javascript:go("Hos.htm")>Hos</a> <a class=black href=javascript:go("Joe.htm")>Joe</a> <a class=black href=javascript:go("Amo.htm")>Amo</a> <a class=black href=javascript:go("Oba.htm")>Oba</a> <a class=black href=javascript:go("Jon.htm")>Jon</a> <a class=black href=javascript:go("Mic.htm")>Mic</a><br><a class=black href=javascript:go("Nah.htm")>Nah</a> <a class=black href=javascript:go("Hab.htm")>Hab</a> <a class=black href=javascript:go("Zep.htm")>Zep</a> <a class=black href=javascript:go("Hag.htm")>Hag</a> <a class=black href=javascript:go("Zec.htm")>Zec</a> <a class=black href=javascript:go("Mal.htm")>Mal</a>;',
'',
'<a class=black href=javascript:go("Mat.htm")>Mat</a> <a class=black href=javascript:go("Mrk.htm")>Mrk</a> <a class=black href=javascript:go("Luk.htm")>Luk</a> <a class=black href=javascript:go("Joh.htm")>Joh</a>;',
'<a class=black href=javascript:go("Act.htm")>Act</a> <a class=black href=javascript:go("Rom.htm")>Rom</a> <a class=black href=javascript:go("1Co.htm")>1Co</a> <a class=black href=javascript:go("2Co.htm")>2Co</a> <a class=black href=javascript:go("Gal.htm")>Gal</a> <a class=black href=javascript:go("Eph.htm")>Eph</a><br><a class=black href=javascript:go("Phi.htm")>Phi</a> <a class=black href=javascript:go("Col.htm")>Col</a>;',
'<a class=black href=javascript:go("1Th.htm")>1Th</a> <a class=black href=javascript:go("2Th.htm")>2Th</a> <a class=black href=javascript:go("1Ti.htm")>1Ti</a> <a class=black href=javascript:go("2Ti.htm")>2Ti</a> <a class=black href=javascript:go("Tit.htm")>Tit</a> <a class=black href=javascript:go("Phm.htm")>Phm</a>;',
'<a class=black href=javascript:go("Heb.htm")>Heb</a> <a class=black href=javascript:go("Jam.htm")>Jam</a> <a class=black href=javascript:go("1Pe.htm")>1Pe</a> <a class=black href=javascript:go("2Pe.htm")>2Pe</a> <a class=black href=javascript:go("1Jo.htm")>1Jo</a> <a class=black href=javascript:go("2Jo.htm")>2Jo</a><br><a class=black href=javascript:go("3Jo.htm")>3Jo</a> <a class=black href=javascript:go("Jud.htm")>Jud</a> <a class=black href=javascript:go("Rev.htm")>Rev</a>']],
['Home--a.htm',[]],
['Hide--blank.htm',[]]
]

// XP Menu object.
var xpmenu_div
var xpmenu_visible=0
// Position getters.
function leftPos(o)
{
  var i=o.offsetLeft
  for(;;){o=o.offsetParent;if(!o)return i;i+=o.offsetLeft}
}
function topPos(o)
{
  var i=o.offsetTop
  for(;;){o=o.offsetParent;if(!o)return i;i+=o.offsetTop}
}
// Initialize.
function xpmenu_init()
{
  try{
  xpmenu_div=document.createElement('div')
  xpmenu_div.style.position='absolute'
  xpmenu_div.style.zIndex='100'
  xpmenu_div.style.visibility='hidden'
  xpmenu_div.style.left='0'
  xpmenu_div.style.top='-1000'
  onload_add(xpmenu_init2)
  }catch(e){ex('xpmenu_init',e)}
}
xpmenu_init()
function xpmenu_init2()
{
  try{
  var o=document.getElementsByTagName('body')
  if(o)o[0].appendChild(xpmenu_div)
  else setTimeout("xpmenu_init2()", 100)
  }catch(e){ex('xpmenu_init2',e)}
}
// Break up an encoded menu item text into its javascript code or href.
// Returns [Javascript code, Menu item text]
// Always assume js code are double-quote safe.
function xpmenu_parse_item(s)
{
  try{
  var j,js=""
  if((j=s.indexOf('--'))!=-1)
  {
    js="go('"+s.substring(j+2)+"');"
    s=s.substring(0,j)
  }
  else if((j=s.indexOf('=='))!=-1)
  {
    js=s.substring(j+2)
    s=s.substring(0,j)
  }
  return [js,s]
  }catch(e){ex("xpmenu_parse_item",e)}
  return ["",""]
}
function xpmenu_get_html(items)
{
  try{
  if(items)xpmenu_items=items
  else items=xpmenu_items

  var s='<table class=graybox style="border-top:1px solid white;border-left:none;border-right:none" cellspacing=0 cellpadding=0><tr><td><table cellspacing=0 cellpadding=0><tr><td height=4 colspan=3></td></tr><tr><td width=2></td><td>'
  var i
  for(i=0;i<items.length;i++)
  {
    var a='xpmenu_items['+i+'][1]'
    var item=xpmenu_parse_item(items[i][0])
    s+='<td class=small'
      +' style="padding:2px;padding-left:8px;padding-right:8px;'
      +'margin:0px;cursor:pointer;"'
      +' onmouseover="xpmenu_mouseover(this,'+a+',event)")"'
      +' onmouseout="xpmenu_mouseout(this)"'
      +' onclick="xpmenu_show(this,'+a+',event);'+item[0]+'"'
      +'>'+item[1]+'</td>'
  }
  s+='</td><td width=4></td></tr><tr><td height=4 colspan=3></td></tr></table></td><td align=right style=padding-right:5px nowrap>'
  
  // Search box.
  s+="<b><a target=main class=small href=vsearch.htm>Search</a></b>"
    +" <input name=ss type=text style=width:200px"
    +" onfocus=hotkeys_disable();this.select() onblur=hotkeys_enable()"
    +" onkeypress=\"var k=keypresscode(event);"
    +"if(k==13)go_search();else if(k==27)this.blur()\">"
    +" <input type=button value=Go onclick=go_search()>"
  return s+'</td></tr></table>'
  }catch(e){ex('xpmenu_get_html',e)}
  return ''
}
function xpmenu_mouseover(obj,a,ev)
{
  try{
  obj.style.backgroundColor='#B2B4BF'
  if(xpmenu_visible)
  {
    xpmenu_visible=0
    xpmenu_show(obj,a,ev)
  }
  }catch(e){ex('xpmenu_mouseover',e)}
}
function xpmenu_mouseout(obj)
{
  try{
  obj.style.backgroundColor=''
  }catch(e){ex('xpmenu_mouseover',e)}
}
function xpmenu_overitem(obj)
{
  try{
  obj.style.backgroundColor='#B2B4BF'
  }catch(e){ex('xpmenu_mouseover',e)}
}
function xpmenu_outitem(obj)
{
  try{
  obj.style.backgroundColor=''
  }catch(e){ex('xpmenu_mouseover',e)}
}
function xpmenu_remain(ev)
{
  // Terminate this event.
  try{
  if(window.event)event.cancelBubble=true
  else if(ev.stopPropagation)ev.stopPropagation()
  }catch(e){}
}
function xpmenu_show(obj,a,ev)
{
  try{
  obj.blur()
  xpmenu_remain(ev)
  // Draw this drop-down menu.
  var i,s='<table cellpadding=0 cellspacing=0 onclick=xpmenu_remain(event) style="border:1px solid #9D9DA1;padding:3px;cursor:pointer;background-color:white">'
  for(i=0;i<a.length;i++)
  {
    if(a[i])
    {
      var item=xpmenu_parse_item(a[i])
      s+='<tr><td class=small style="padding:3px;margin:0px;padding-left:20px;padding-right:60px;" onmouseover="xpmenu_overitem(this)" onmouseout="xpmenu_outitem(this)" onclick="xpmenu_hide();'+item[0]+'">'+item[1]+'</td></tr>'
    }
    else s+='<tr><td height=3></td></tr><tr><td height=1 style="background-color:#9D9DA1"></td></tr><tr><td height=5></td></tr>'
  }
  s+='</div>'
  xpmenu_div.innerHTML=s
  // Hide if already visible.
  if(xpmenu_visible){xpmenu_hide();return}
  // Place and make visible.
  xpmenu_div.x=leftPos(obj)
  xpmenu_div.y=topPos(obj)
  xpmenu_div.style.left=xpmenu_div.x+'px'
  xpmenu_div.style.top=(xpmenu_div.y+obj.offsetHeight)+'px'
  xpmenu_div.style.visibility='visible'
  xpmenu_visible=1
  }catch(e){ex('xpmenu_show',e)}
}
function xpmenu_hide()
{
  try{
  xpmenu_div.style.visibility='hidden'
  xpmenu_div.style.y='-1000'
  xpmenu_visible=0
  }catch(e){ex('xpmenu_hide',e)}
}
onclick_add(xpmenu_hide)
