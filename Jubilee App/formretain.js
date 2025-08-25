//To use, simply put: <script src=formretain.js>/script> in any HTML page
//Saves all values that should be saved (see comments below).

//Time in days to save form fields values after last visit
//Set to different value to reset cookie (ie: "101 days" instead of "100 days"):
var EOV="EndOfValues"
var memoryduration="100 days"
var formvalueseparator="\x01"//char unicode 1 & 2
var cookiename="FormValues"+location.pathname
var cookietail=";path=/;expires="
var DUMPCOOKIES=0
// Remember all of the following stuff:
// 1. <input type={checkbox|hidden|radio|text}>
// 2. <textarea>
// 3. <select>
// Only grabs those elements that has a defined name.
// Save cookie value name as "formnameornum:ename=evalue"
function frSetForm()
{
  try{
  var c=document.cookie
  if(DUMPCOOKIES)alert("Cookie String (Length="+c.length+"):\n"+c)
  if(c.length==0)return
  var i=c.indexOf(cookiename+'=')
  if(i==-1)return
  c=unescape(c.substring(i+cookiename.length+1))
  i=c.indexOf(EOV+formvalueseparator+memoryduration)
  if(i<=0)return
  c=c.substring(0,i-1)
  if(!c)return
  var ck=c.split(formvalueseparator)
  if(!ck.length)return
  if(DUMPCOOKIES)alert("Load:\n"+ck.join("\n"))
  var k,f=document.forms
  for(k=0;k<ck.length;k++)
    {
      // Form name/number : element name = element value
      var a=/^(\w+):(\w+)=(.*)$/.exec(ck[k])
      if(!a)continue//ignore
      var e,fnamenum=a[1],ename=a[2],v=unescape(a[3])
      try{e=f[fnamenum][ename]}catch(e){continue}
      if(!e)continue
      // Get tag name.
      var tag=(e.tagName?e.tagName:e[0].tagName).toLowerCase()
      // Set element value.
      if(tag=='select')
        {
          if(!e.options)continue
          for(var j=0;j<e.options.length;j++)
            if(e.options[j].value==v){e.selectedIndex=j;break}
        }
      else if(tag=='textarea')
        e.value=v
      else if(tag=='input')
        {
          // Get element type.
          var ty=e.length?e[0].type:e.type
          ty=ty.toLowerCase()
          if(ty=='checkbox')
            {
              v=v.toLowerCase()
              e.checked=(v=='true'||v=='on'||v=='1'||v==1)
            }
          else if(ty=='radio')
            {
              for(var m=0;m<e.length;m++)
                e[m].checked=(e[m].value==v)
            }
          else if(ty=='hidden'||ty=='text')
            e.value=v
        }
    }
  }catch(e){alert("setformvalues() exception: "+e.message)}
}
function frSaveForm()
{
  try{
  var i,j,k,t,e,a=[],f=document.forms
  for(i=0;i<f.length;i++)
    {
      var fnamenum=f[i].name?f[i].name:i
      for(j=0;j<f[i].elements.length;j++)
        {
          var e=f[i].elements[j]
          t=e.tagName.toLowerCase()
          var n=t!='select'&&e.length?e[0].name:e.name
          if(n=='')continue
          var ty=t=='select'?'select':e.type.toLowerCase()
          var flag=0
          if(t=='textarea'){flag=1;t=e.value}
          else if(t=='select')
            {
              flag=1
              for(k=0;k<e.options.length;k++)
                if(e.options[k].selected)
                  {t=e.options[k].value;break}
            }
          else if(t=='input')
            {
              if(ty=='checkbox'){flag=1;t=e.checked?'true':'false'}
              else if(ty=='radio'){if(e.checked){flag=1;t=e.value}}
              else if(ty=='hidden'||ty=='text'){flag=1;t=e.value}
            }
          if(flag)a.push(fnamenum+':'+n+'='+escape(t))
        }
    }
  a.push(EOV)//required
  a.push(memoryduration)//required
  if(DUMPCOOKIES)alert("Save:\n"+a.join("\n"))
  a=a.join(formvalueseparator)
  var expireDate=new Date()
  expireDate.setDate(expireDate.getDate()+parseInt(memoryduration))
  document.cookie=cookiename+"="+escape(a)+cookietail+expireDate.toGMTString()
  }catch(f){alert("frSaveForm() exception: "+f.message)}
}
function frInit()
{
  try{
  try{onload_add(frSetForm)}catch(e){window.onload=frSetForm}
  try{onunload_add(frSaveForm)}catch(e){window.onunload=frSaveForm}
  }catch(e){alert("frInit() exception: "+e.message)}
}
frInit()
