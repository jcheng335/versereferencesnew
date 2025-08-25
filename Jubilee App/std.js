// std.js: standard javascript functions for common use.

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
  setTimeout('top.document.title=exception_shown',100000)
  }catch(g){alert(g.message)}
}
////////////////////////////////////////////////////////////////////
// Converts a string to an integer. Don't use parseInt() becos it returns NaN.
function int(s)
{
  var i=0
  try{if(isNaN(i=parseInt(s)))i=0}catch(e){}
  return i
}
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
// Standard onclick handlers to support multiple handlers.
var onclick_funcs=[]
function onclick_add(func)
{
  try{
  onclick_funcs.push(func)
  document.onclick=onclick_funcs.length==1?func:onclick_handler
  }catch(e){ex('onclick_add',e)}
}
// Invoke all the added event handler functions.
function onclick_handler(e)
{
  for(var i=0;i<onclick_funcs.length;i++)
    {try{onclick_funcs[i](e)}catch(e){ex('onclick_handler',e)}}
}
////////////////////////////////////////////////////////////////////
// Dynamic load a Javascript file.
var seen_js_fname=[]
function load_js(fname,code)
{
  try{
  if(seen_js_fname[fname])return setTimeout(code,1)
  seen_js_fname[fname]=1
  run_js(fname,code)
  }catch(e){ex("load_js",e)}
}
function run_js(fname,code)
{
  try{
  resume_js_code=code
  var e=document.createElement('script')
  e.src=fname
  document.getElementsByTagName('head')[0].appendChild(e)
  }catch(f){ex("run_js",f)}
}
// Resume execution after loading a Javascript file.
var resume_js_code=""
function resume_js()
{
  try{if(resume_js_code){setTimeout(resume_js_code,1);resume_js_code=""}}
  catch(e){ex("resume_js",e)}
}
////////////////////////////////////////////////////////////////////
// String escapes.
function hex1(i)
{
  if(i>=0&&i<=9)return String.fromCharCode(48+i)
  if(i>=10&&i<=15)return String.fromCharCode(55+i)
  return "\n"
}
function hex2(i){return hex1(Math.floor(i/16))+hex1(i%16)}
function xesc(s)
{
  var t=""
  while(s.length)
  {
    var i=s.charCodeAt(0)
    t+=i>127?"\\x"+hex2(i):s.charAt(0)
    s=s.substring(1)
  }
  return t
}
function qesc(s){return xesc(s.replace(/([\\\'])/g,"\\$1"))}
function qqesc(s){return xesc(s.replace(/([\\\"])/g,"\\$1"))}
////////////////////////////////////////////////////////////////////
// Counting time. getmillis() is a very slow function.
function getmillis(){return new Date().getTime()}
// Returns nicely-formatted seconds taken.
function timetaken(start)
{
  try{
  var sec=''+((new Date().getTime()-start)/1000)
  var i=sec.indexOf('.')
  if(i==-1)return sec+'.000'
  return sec+"000".substring(0,4-sec.length+i)
  }catch(e){ex("timetaken",e)}
}
////////////////////////////////////////////////////////////////////
// Uppercase first character and lowercase the rest of the string.
function ucfirst(s)
{
  if(s.length==0)return s
  if(s.length==1)return s.toUpperCase()
  return s.charAt(0).toUpperCase()+s.substring(1).toLowerCase()
}
////////////////////////////////////////////////////////////////////
