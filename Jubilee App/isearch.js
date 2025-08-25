// isearch.js: indexed-search.

// todo:
// - add options to vsearch.htm
// - complete idata.js functions

// Indexed-search algorithm:
// - Get search options.
// - Get search string.
// - Short-circuit: if no search string, done.
// - Check results cache: if search already cached, done.
// - Load WW (array of all keywords)
// - Short-circuit: if any keywords to find do not exist, done.
// - Get all keyword index data.
// - Intersect all keyword index data.
// - Show search results incrementally.
// (for more details, look at the code itself)

////////////////////////////////////////////////////////////////////
// Top-level user-entry function.
function isearch()
{
  try{
  init_search_vars()
  if(get_search_options())return
  if(get_sstr())return
  if(check_cache())return
  
  // Form regexes for highlighting keywords only.
  var r_opt=opt_mc?"g":"ig"
  var s1=opt_ww?"(^|[^a-zA-Z</])(":"()("
  var s2=opt_ww?")($|[^a-zA-Z>])":")()"
  for(i=0;i<sarray.length;i++)
    sregex.push(new RegExp(s1+sarray[i]+s2,r_opt))

  sresults_sregex[scachekey]=sregex
  
  main.document.getElementById("cancelbutton").style.visibility="visible"
  setstat("Searching for `<u>"+sstr+"</u>'")

  load_js("ww.js","isearch_1()")
  }catch(e){ex("isearch",e)}
}
function isearch_1()
{
  try{
  if(sstr_not_exists())return
  load_all_keywords("isearch_2()")
  }catch(e){ex("isearch_1",e)}
}
function isearch_2()
{
  try{
  intersect_all_keywords()
  show_search_results()
  }catch(e){ex("isearch_2",e)}
}
////////////////////////////////////////////////////////////////////
// All search variables.
var sstr,sresults,sarray,sregex,sstartmillis,skeywords,
    sresultscache=[],sresults_sregex=[],scachekey,search_canceled
// All search options.
var opt_mc,opt_ww,opt_st,opt_vv,opt_fn,opt_bk1,opt_bk2
////////////////////////////////////////////////////////////////////
// Initialize all search variables.
function init_search_vars()
{
  try{
  sstr=""
  sresults=[]
  sarray=[]
  sregex=[]
  sstartmillis=getmillis()
  skeywords=[]
  scachekey=""
  search_canceled=0
  }catch(e){ex("init_search_vars",e)}
}
////////////////////////////////////////////////////////////////////
// Get all the search options.
// Returns 1 if nothing to search for.
function get_search_options()
{
  try{
  var f=main.document.f
  
  // Read options.
  opt_mc=f.mc.checked?1:0
  opt_ww=f.ww.checked?1:0
  opt_st=f.st.checked?1:0
  opt_vv=f.vv.checked?1:0
  opt_fn=f.fn.checked?1:0

  if(f.bk.checked)
  {
    opt_bk1=f.bk1.options.selectedIndex
    opt_bk2=f.bk2.options.selectedIndex
  }
  else
  {
    opt_bk1=0
    opt_bk2=65
  }

  // Check options.
  if((!opt_st&&!opt_vv&&!opt_fn)||(opt_bk1>opt_bk2))
    return end_search("Search options indicate nothing to search for")
    
  }catch(e){ex("get_search_options",e)}
  return 0
}
////////////////////////////////////////////////////////////////////
// Get the search string and breaks it up into separate words.
// Returns 1 if search not necessary.
function get_sstr()
{
  try{
  // Get and trim string.
  var ss=main.document.f.ss
  ss.value=sstr=ss.value
    .replace(/^\s+/,'') // left trim
    .replace(/\s+$/,'') // right trim
    .replace(/[^a-zA-Z]/g,' ') // trim invalid characters
    .replace(/[\s\xA0]{2,}/g,' ') // trim extra spaces

  // Short-circuit if sstr is empty.
  if(sstr.length==0)
    return end_search("Nothing to search for")
  
  // Break into array of keywords and regexes for highlighting them.
  var i,a=sstr.split(' '),seen=[]
  for(i=0;i<a.length;i++)
  {
    var s=opt_mc?a[i]:a[i].toLowerCase()
    if(seen[s])continue
    seen[s]=1
    sarray.push(s)
  }
  sarray=sarray.sort()
  
  // Generate cache key.
  scachekey=sarray.join(' ')
    +'OPT:'+opt_mc+opt_ww+opt_st+opt_vv+opt_fn+' '+opt_bk1+' '+opt_bk2
  
  }catch(e){ex("get_sstr",e)}
  return 0
}
////////////////////////////////////////////////////////////////////
// Check whether the current search has already been cached or not.
// If cached, shows results and returns 1.
var was_cached
function check_cache()
{
  try{
  was_cached=0
  if(sresultscache[scachekey])
  {
    was_cached=1
    sresults=sresultscache[scachekey]
    sregex=sresults_sregex[scachekey]
    show_search_results()
    return 1
  }
  }catch(e){ex("check_cache",e)}
  return 0
}
////////////////////////////////////////////////////////////////////
// Check in WW[] to see whether the search string exists at all or not.
// If no exists, shows results and returns 1.
function sstr_not_exists()
{
  try{
  var no_such_words=[]
  for(var i=0;i<sarray.length;i++)
  {
    var a=ww_get_words(sarray[i],opt_mc,opt_ww)
    if(!a||a.length==0)no_such_words.push(sarray[i])
    if(no_such_words.length==0)skeywords.push(a)
  }
  if(no_such_words.length)
    return end_search("Keyword"+(no_such_words.length==1?"":"s")
      +" `"+no_such_words.join(", ")
      +"' do"+(no_such_words.length==1?"es":"")+" not appear at all")

  }catch(e){ex("sstr_not_exists",e)}
  return 0
}
////////////////////////////////////////////////////////////////////
// Load the index data for all the keywords to find.
// Calls the `return_func' when done.
var cur_load_grps,ld_return_func
function load_all_keywords(return_func)
{
  try{
  ld_return_func=return_func
  cur_load_grps=[]
  var seen=[]
  for(var i=0;i<skeywords.length;i++)
    for(var j=0;j<skeywords[i].length;j++)
    {
      var grp=WW[skeywords[i][j].toLowerCase()][0]
      if(!seen[grp]){seen[grp]=1;cur_load_grps.push(grp)}
      if(search_canceled)return canceled_search()
    }
  load_next_keyword()
  }catch(e){ex("load_all_keywords",e)}
}
function load_next_keyword()
{
  try{
  if(search_canceled)return canceled_search()
  if(cur_load_grps.length==0){setTimeout(ld_return_func,1);return}
  load_js("idx-kw/"+cur_load_grps.pop()+".js","load_next_keyword()")
  }catch(e){ex("load_next_keyword",e)}
}
////////////////////////////////////////////////////////////////////
// Gets all the index data for all the keywords to find,
// and intersects them all to get the search results.
function intersect_all_keywords()
{
  try{
  var a,i,j,vref,res=[],something
  // Merge the vrefs within each keyword group first.
  for(i=0;i<skeywords.length;i++)
  {
    for(a=[],something=0,j=skeywords[i].length-1;j>=0;j--)
      for(var vref in KW[skeywords[i][j]])
      {
        // Filter by search options.
        if(key_is_verse(vref))         {if(!opt_vv)continue}
        else if(key_is_footnote(vref)) {if(!opt_fn)continue}
        else                           {if(!opt_st)continue}
        
        var bk=codenum(vref.charCodeAt(0))
        if(bk<opt_bk1||bk>opt_bk2)continue
        
        // Intersect here.
        if(i==0||res[vref])a[vref]=something=1
        
        if(search_canceled)return canceled_search()
      }
    res=a
    if(something==0)break
  }
  // Save all search results as an array.
  for(vref in res)sresults.push(vref)
  sresults=sresults.sort()
  }catch(e){ex("intersect_all_keywords",e)}
}
////////////////////////////////////////////////////////////////////
// Displays all results in an incremental way.
// Always calls end_search().
var current_result_index
function show_search_results()
{
  try{
  // Indicate which result is currently being loaded.
  current_result_index=0
  
  // Save in cache.
  if(!was_cached)
  {
    sresultscache[scachekey]=sresults
    sresults_sregex[scachekey]=sregex
  }
  // Update status first.
  was_cached=was_cached?"(cached)":""
  if(sresults.length==0)
    return end_search("String `<u>"+sstr+"</u>' not found",was_cached)

  setstat("String `<u>"+sstr+"</u>' found <b>"
    +sresults.length+"</b> time"
    +(sresults.length==1?"":"s")
    +" - "+timetaken(sstartmillis)+" sec. "
    +(was_cached?was_cached:""))
  
  // Print out all DHTML filler elements first.
  var i,s=""
  for(var i=1;i<=sresults.length;i++)
    s+="<p id=p"+i+"></p>"
  main.document.getElementById('results').innerHTML=s  

  // Display all results in the left bar.
  var i,s="<q><a target=main href=vsearch.htm?ss="+escape(sstr)
    +">Search for `<u>"+sstr+"</u>' returned "+sresults.length+" results</a></q>"
  for(i=0;i<sresults.length;)
  {
    var a=keyvref(sresults[i++])
    s+=getshownum(i)+") <a target=main href="+a[1]+">"+a[0]+"</a><br>"
  }
  left.document.body.innerHTML=s
  
  // Link to show left panel.
  if(document.data.leftbar_on.value!='1'&&!show_hide_link_printed)
  {
    show_hide_link_printed=1
    debug("<a href=javascript:exec('tgshow(\"leftbar\")')>Show/Hide Search Results Panel</a>")
  }

  setTimeout("show_search_results_1()",1)
  }catch(e){ex("show_search_results",e)}
}
// Wait till all the fillers are loaded.
function show_search_results_1()
{
  try{
  if(search_canceled)return canceled_search()
  var o=main.document.getElementById('p'+sresults.length)
  return show_search_results_2()
  }catch(e){}
  setTimeout("show_search_results_1()",1)
}
// Load the data for the next result.
function show_search_results_2()
{
  try{
  if(search_canceled)return canceled_search()
  var i=current_result_index
  if(i>=sresults.length)return show_search_results_4()
  load_js("idx-bd/"+keyhash(sresults[i])+".js","show_search_results_3()")
  }catch(e){ex("show_search_results_2",e)}
}
// Fill in the missing text data.
function show_search_results_3()
{
  try{
  var key=sresults[current_result_index++]
  var a=keyvref(key)
  var i=current_result_index
  
  if(search_canceled)return canceled_search()
  main.document.getElementById('p'+i).innerHTML=
     "<s onclick=hi("+i
    +") onmouseover=hi1() onmouseout=ns()>"+getshownum(i)+")</s> "
    +"<b><a href="+a[1]+">"+a[0]+"</a></b>"+"<a onclick=rm("+i
    +") onmouseover=rm1() onmouseout=ns()>&nbsp;&nbsp;</a>"
    +hilite_words(BD[key])

  setTimeout("show_search_results_2()",1)
  }catch(e){ex("show_search_results_3",e)}
}
// Get final timing.
var show_hide_link_printed=0
function show_search_results_4()
{
  try{
  end_search("String `<u>"+sstr+"</u>' found <b>"
    +sresults.length+"</b> time"
    +(sresults.length==1?"":"s"),was_cached)
  }catch(e){ex("show_search_results_4",e)}
}
// Highlight all the search keywords.
function hilite_words(vt)
{
  if(!vt)return "?"
  for(var i=sregex.length-1;i>=0;i--)
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
////////////////////////////////////////////////////////////////////
// Finalize the search.
function canceled_search()
{
  try{
  var s=main.document.getElementById("status").innerHTML
  return end_search((s?s+" - ":"")+"Searched canceled")
  }catch(e){ex("canceled_search",e)}
}
function end_search(s,t)
{
  try{
  // Restore search form to after-search condition.
  setstat(s+" - "+timetaken(sstartmillis)+" sec. "+(t?t:""))
  main.document.getElementById("cancelbutton").style.visibility="hidden"
  main.document.f.ss.select()
  }catch(e){}
  return 1
}
////////////////////////////////////////////////////////////////////
