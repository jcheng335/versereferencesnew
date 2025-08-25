// main.js: javascript stuff for pages in the `main' frame.

////////////////////////////////////////////////////////////////////
// Standard exception handler.
var exception_shown="" // show only once
function ex(f,e)
{
  try{
  if(exception_shown.length)return
  exception_shown=top.document.title
  var s=f+"(): "+e.message
  top.document.title=exception_shown+'  ['+s+']'
  top.status=s
  setTimeout('top.document.title=exception_shown',10000)
  }catch(g){alert(g.message)}
}
////////////////////////////////////////////////////////////////////
var init_js_stuff=/\bframes\.htm$/i.test(parent.location.pathname)

// Put this page into frame.
function put_in_frame()
{
  try{if(/\bframes\.htm$/i.test(parent.location.pathname))return}catch(e){}
  location.href='frames.htm?'+location.href.replace(/^.*[\\\/]/,"")
}

if(/\bvsearch\.htm$/i.test(location.pathname)
   || /\blistv\.htm$/i.test(location.pathname))
  put_in_frame()
////////////////////////////////////////////////////////////////////
// Standard onload handlers to support multiple handlers.
var onload_funcs=[]
function onload_add(func)
{
  try{
  onload_funcs.push(func)
  window.onload=onload_funcs.length==1?func:onload_handler
  }catch(e){ex('onload_add',e)}
}
// Invoke all the added event handler functions.
function onload_handler(e)
{
  for(var i=0;i<onload_funcs.length;i++)
    {try{onload_funcs[i](e)}catch(e){ex('onload_handler:'+i,e)}}
}
////////////////////////////////////////////////////////////////////
// Retrieve GET param.
var get_params=null
function get_param(varname)
{
  try{
  if(get_params==null)
  {
    if(location.search.length<=1)return ""
    
    var s=location.search.substring(1)
    var a=s.split('&')

    get_params=[]
    for(var i=0;i<a.length;i++)
    {
      var j=a[i].indexOf('=')
      if(j==-1)get_params[a[i]]=""
      else get_params[a[i].substring(0,j)]=
        unescape(a[i].substring(j+1)).replace(/\+/g,' ')
    }
  }
  return get_params[varname]
  }catch(e){ex("get_param",e)}
}
////////////////////////////////////////////////////////////////////
// Executes a piece of code in the parent frame.
function exec(code)
{
  if(!init_js_stuff)return
  try{parent.document.getElementById('exec').innerHTML+=';'+escape(code)}
  catch(e){top.status="code failed: "+code+": "+e.message}
}
////////////////////////////////////////////////////////////////////
// Used for hiding the xpmenu when the page is clicked on.
if(init_js_stuff)
document.onclick=function(){exec("xpmenu_hide()")}
////////////////////////////////////////////////////////////////////
if(/\b(([123A-Z]\w\w[ON]?)|(about)|(bkinfo))\.htm$/.test(location.pathname))
document.write(
"<style>b,i,p,q,s,em,h1,h2,h3,h4,h5,h6,tt,big,del,dfn,kbd,ins,sub,sup,var,"
+"cite,code,samp,abbr,body{font-family:times}"
+"/* Darken anchor.  */"
+".o,a.o:hover,a.o:visited{color:black}"
+"/* Gray box.  */"
+"div{border:1px solid #dddddd;"
+"background-color:#fcfcfc;padding:2px;padding-left:30px;"
+"margin-right:2px;margin-top:6px;margin-bottom:6px}"
+"/* Blue box.  */"
+"h4{background-color:#f9f9f9;padding:3px;font-family:tahoma;font-size:85%;"
+"margin-top:6px;margin-bottom:6px;border:1px solid #dddddd;font-weight:normal}"
+"/* Don't show verse links.  */"
+".nd{display:none}"
+"/* Outline text in verses.  */"
+"h1,tt,h5,del,var,code{font-weight:normal;display:block;text-indent:-30px}"
+"/* ot1 */ h1{margin-left:40px;font-weight:bold}"
+"/* ot2 */ tt{margin-left:70px} tt.psa{text-indent:0px;margin-left:30px}"
+"/* ot3 */ h5{margin-left:100px}"
+"/* ot4 */ del{margin-left:130px}"
+"/* ot5 */ var{margin-left:160px}"
+"/* ot6 */ code{margin-left:190px}"
+"/* Outline text in outline listing.  */"
+"kbd,em,h6,dfn,big,samp{font-weight:normal;display:block;text-indent:-30px}"
+"/* ol1 */ kbd{margin-left:40px;font-weight:bold;}"
+"/* ol2 */ em{margin-left:70px} em.psa{text-indent:0px;margin-left:30px}"
+"/* ol3 */ h6{margin-left:100px}"
+"/* ol4 */ dfn{margin-left:130px}"
+"/* ol5 */ big{margin-left:160px}"
+"/* ol6 */ samp{margin-left:190px}"
+"/* Intro para.  */"
+"ins{font-family:verdana;text-indent:-20px;font-size:80%;"
+"margin-left:50px;margin-right:30px;margin-bottom:3px}"
+"/* Main title.  */"
+"pre{font-family:arial;font-size:130%}"
+"</style>")

if(init_js_stuff)
  document.write("<style>body{margin:0px;margin-right:6px}</style>")

function sups_toggler()
{
  document.write('<a href=javascript:hotkey_sups()>'
    +'Toggle All Superscripts (T)</a>')
}
////////////////////////////////////////////////////////////////////
// List of hotkeys to focus on different textbox objects.
function hotkey_ss(){exec("hotkey_ss()")}
function hotkey_vr(){exec("hotkey_vr()")}
function hotkey_gv(){exec("hotkey_gv()")}
function hotkey_esc(){exec("hide_all_panels()")}
function hotkey_sups()
{
  try{
  a=document.getElementsByTagName("s")
  if(a.length)
  {
    var s="none"
    if(a[0].style.display==s)s=""
    for(var i=0;i<a.length;i++)a[i].style.display=s
  }
  }catch(e){ex("tg_all_sups",e)}
}

var HotKeys={s:hotkey_ss,S:hotkey_ss,'/':hotkey_ss,l:hotkey_vr,
L:hotkey_vr,g:hotkey_gv,G:hotkey_gv,"\x1B":hotkey_esc,
t:hotkey_sups,T:hotkey_sups}

function hotkeys(e)
{
  try{
  if(window.event)e=window.event
  var c=String.fromCharCode(e.keyCode?e.keyCode:e.charCode)
  if(HotKeys[c])
  {
    // IE puts the key into the input box! (Bad)
    try{if(e.keyCode)e.keyCode=0}catch(e){}
    HotKeys[c]()
  }
  }catch(e){ex("hotkeys",e)}
}
document.onkeypress=hotkeys
// Use for onfocus and onblur in textboxes.
function hotkeys_disable(){document.onkeypress=null}
function hotkeys_enable(){document.onkeypress=hotkeys}
////////////////////////////////////////////////////////////////////
// Update quick links.
function update_quick_links()
{
  var basename=location.pathname.replace(/^.*[\\\/]/,'').replace(/\.htm$/,'')
  if(basename=='leftbar'||basename=='rightbar')return
  exec("quick_links()")
}
if(init_js_stuff)
  onload_add(update_quick_links)
////////////////////////////////////////////////////////////////////
