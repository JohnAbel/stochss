var g=document,k=Array,l=Error,aa=parseInt,n=String;function p(a,b){return a.currentTarget=b}function q(a,b){return a.keyCode=b}function r(a,b){return a.disabled=b}
var s="push",t="shift",u="slice",v="replace",w="value",x="preventDefault",y="indexOf",z="keyCode",A="type",ba="name",B="toString",C="length",ca="propertyIsEnumerable",D="prototype",da="checked",E="split",F="style",ea="target",G="call",H="apply",I,J=this,K=function(a){var b=typeof a;if("object"==b)if(a){if(a instanceof k)return"array";if(a instanceof Object)return b;var c=Object[D][B][G](a);if("[object Window]"==c)return"object";if("[object Array]"==c||"number"==typeof a[C]&&"undefined"!=typeof a.splice&&
"undefined"!=typeof a[ca]&&!a[ca]("splice"))return"array";if("[object Function]"==c||"undefined"!=typeof a[G]&&"undefined"!=typeof a[ca]&&!a[ca]("call"))return"function"}else return"null";else if("function"==b&&"undefined"==typeof a[G])return"object";return b},fa=function(a){var b=K(a);return"array"==b||"object"==b&&"number"==typeof a[C]},L=function(a){return"string"==typeof a},ga=function(a){var b=typeof a;return"object"==b&&null!=a||"function"==b},ha=function(a,b){var c=k[D][u][G](arguments,1);
return function(){var b=c[u]();b[s][H](b,arguments);return a[H](this,b)}},ia=function(a,b){function c(){}c.prototype=b[D];a.t=b[D];a.prototype=new c;a.A=function(a,c,e){return b[D][c][H](a,k[D][u][G](arguments,2))}};var M=function(a){if(l.captureStackTrace)l.captureStackTrace(this,M);else{var b=l().stack;b&&(this.stack=b)}a&&(this.message=n(a))};ia(M,l);M[D].name="CustomError";var ja=function(a,b){for(var c=a[E]("%s"),d="",f=k[D][u][G](arguments,1);f[C]&&1<c[C];)d+=c[t]()+f[t]();return d+c.join("%s")},ra=function(a,b){if(b)a=a[v](ka,"&amp;")[v](la,"&lt;")[v](ma,"&gt;")[v](na,"&quot;")[v](oa,"&#39;")[v](pa,"&#0;");else{if(!qa.test(a))return a;-1!=a[y]("&")&&(a=a[v](ka,"&amp;"));-1!=a[y]("<")&&(a=a[v](la,"&lt;"));-1!=a[y](">")&&(a=a[v](ma,"&gt;"));-1!=a[y]('"')&&(a=a[v](na,"&quot;"));-1!=a[y]("'")&&(a=a[v](oa,"&#39;"));-1!=a[y]("\x00")&&(a=a[v](pa,"&#0;"))}return a},ka=/&/g,
la=/</g,ma=/>/g,na=/"/g,oa=/'/g,pa=/\x00/g,qa=/[\x00&<>"']/,sa=function(a,b){return a<b?-1:a>b?1:0},ta=function(a){return n(a)[v](/\-([a-z])/g,function(a,c){return c.toUpperCase()})},ua=function(a,b){var c=L(b)?n(b)[v](/([-()\[\]{}+?*.$\^|,:#<!\\])/g,"\\$1")[v](/\x08/g,"\\x08"):"\\s";return a[v](new RegExp("(^"+(c?"|["+c+"]+":"")+")([a-z])","g"),function(a,b,c){return b+c.toUpperCase()})};var va=function(a,b){b.unshift(a);M[G](this,ja[H](null,b));b[t]()};ia(va,M);va[D].name="AssertionError";var N=function(a,b,c){if(!a){var d="Assertion failed";if(b)var d=d+(": "+b),f=k[D][u][G](arguments,2);throw new va(""+d,f||[]);}return a};var O=k[D],wa=O[y]?function(a,b,c){N(null!=a[C]);return O[y][G](a,b,c)}:function(a,b,c){c=null==c?0:0>c?Math.max(0,a[C]+c):c;if(L(a))return L(b)&&1==b[C]?a[y](b,c):-1;for(;c<a[C];c++)if(c in a&&a[c]===b)return c;return-1},xa=O.forEach?function(a,b,c){N(null!=a[C]);O.forEach[G](a,b,c)}:function(a,b,c){for(var d=a[C],f=L(a)?a[E](""):a,e=0;e<d;e++)e in f&&b[G](c,f[e],e,a)},ya=function(a){var b=a[C];if(0<b){for(var c=k(b),d=0;d<b;d++)c[d]=a[d];return c}return[]},za=function(a,b,c){N(null!=a[C]);return 2>=
arguments[C]?O[u][G](a,b):O[u][G](a,b,c)};var Aa=function(a,b,c){for(var d in a)b[G](c,a[d],d,a)},Ba="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" "),Ca=function(a,b){for(var c,d,f=1;f<arguments[C];f++){d=arguments[f];for(c in d)a[c]=d[c];for(var e=0;e<Ba[C];e++)c=Ba[e],Object[D].hasOwnProperty[G](d,c)&&(a[c]=d[c])}};var P;t:{var Da=J.navigator;if(Da){var Ea=Da.userAgent;if(Ea){P=Ea;break t}}P=""};var Fa=-1!=P[y]("Opera")||-1!=P[y]("OPR"),Q=-1!=P[y]("Trident")||-1!=P[y]("MSIE"),R=-1!=P[y]("Gecko")&&-1==P.toLowerCase()[y]("webkit")&&!(-1!=P[y]("Trident")||-1!=P[y]("MSIE")),S=-1!=P.toLowerCase()[y]("webkit"),Ga=function(){var a=J.document;return a?a.documentMode:void 0},Ha=function(){var a="",b;if(Fa&&J.opera)return a=J.opera.version,"function"==K(a)?a():a;R?b=/rv\:([^\);]+)(\)|;)/:Q?b=/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/:S&&(b=/WebKit\/(\S+)/);b&&(a=(a=b.exec(P))?a[1]:"");return Q&&(b=Ga(),b>
parseFloat(a))?n(b):a}(),Ia={},T=function(a){var b;if(!(b=Ia[a])){b=0;for(var c=n(Ha)[v](/^[\s\xa0]+|[\s\xa0]+$/g,"")[E]("."),d=n(a)[v](/^[\s\xa0]+|[\s\xa0]+$/g,"")[E]("."),f=Math.max(c[C],d[C]),e=0;0==b&&e<f;e++){var h=c[e]||"",m=d[e]||"",eb=RegExp("(\\d*)(\\D*)","g"),fb=RegExp("(\\d*)(\\D*)","g");do{var V=eb.exec(h)||["","",""],W=fb.exec(m)||["","",""];if(0==V[0][C]&&0==W[0][C])break;b=sa(0==V[1][C]?0:aa(V[1],10),0==W[1][C]?0:aa(W[1],10))||sa(0==V[2][C],0==W[2][C])||sa(V[2],W[2])}while(0==b)}b=
Ia[a]=0<=b}return b},Ja=J.document,Ka=Ja&&Q?Ga()||("CSS1Compat"==Ja.compatMode?aa(Ha,10):5):void 0;var La=!Q||Q&&9<=Ka;!R&&!Q||Q&&Q&&9<=Ka||R&&T("1.9.1");Q&&T("9");var Ma=function(a,b){var c;c=a.className;c=L(c)&&c.match(/\S+/g)||[];for(var d=za(arguments,1),f=c[C]+d[C],e=c,h=0;h<d[C];h++)0<=wa(e,d[h])||e[s](d[h]);a.className=c.join(" ");return c[C]==f};var U=function(a,b){return L(b)?a.getElementById(b):b},Na=function(a,b,c,d){a=d||a;var f=b&&"*"!=b?b.toUpperCase():"";if(a.querySelectorAll&&a.querySelector&&(f||c))return a.querySelectorAll(f+(c?"."+c:""));if(c&&a.getElementsByClassName){b=a.getElementsByClassName(c);if(f){a={};for(var e=d=0,h;h=b[e];e++)f==h.nodeName&&(a[d++]=h);a.length=d;return a}return b}b=a.getElementsByTagName(f||"*");if(c){a={};for(e=d=0;h=b[e];e++){var f=h.className,m;if(m="function"==typeof f[E])m=0<=wa(f[E](/\s+/),c);m&&
(a[d++]=h)}a.length=d;return a}return b},Pa=function(a,b){Aa(b,function(b,d){"style"==d?a[F].cssText=b:"class"==d?a.className=b:"for"==d?a.htmlFor=b:d in Oa?a.setAttribute(Oa[d],b):0==d.lastIndexOf("aria-",0)||0==d.lastIndexOf("data-",0)?a.setAttribute(d,b):a[d]=b})},Oa={cellpadding:"cellPadding",cellspacing:"cellSpacing",colspan:"colSpan",frameborder:"frameBorder",height:"height",maxlength:"maxLength",role:"role",rowspan:"rowSpan",type:"type",usemap:"useMap",valign:"vAlign",width:"width"},Ra=function(a,
b,c){var d=arguments,f=d[0],e=d[1];if(!La&&e&&(e[ba]||e[A])){f=["<",f];e[ba]&&f[s](' name="',ra(e[ba]),'"');if(e[A]){f[s](' type="',ra(e[A]),'"');var h={};Ca(h,e);delete h[A];e=h}f[s](">");f=f.join("")}f=g.createElement(f);e&&(L(e)?f.className=e:"array"==K(e)?Ma[H](null,[f].concat(e)):Pa(f,e));2<d[C]&&Qa(g,f,d,2);return f},Qa=function(a,b,c,d){function f(c){c&&b.appendChild(L(c)?a.createTextNode(c):c)}for(;d<c[C];d++){var e=c[d];if(!fa(e)||ga(e)&&0<e.nodeType)f(e);else{var h;t:{if(e&&"number"==typeof e[C]){if(ga(e)){h=
"function"==typeof e.item||"string"==typeof e.item;break t}if("function"==K(e)){h="function"==typeof e.item;break t}}h=!1}xa(h?ya(e):e,f)}}};var Sa=function(a){var b=a[A];if(void 0===b)return null;switch(b.toLowerCase()){case "checkbox":case "radio":return a[da]?a[w]:null;case "select-one":return b=a.selectedIndex,0<=b?a.options[b][w]:null;case "select-multiple":for(var b=[],c,d=0;c=a.options[d];d++)c.selected&&b[s](c[w]);return b[C]?b:null;default:return void 0!==a[w]?a[w]:null}};var Ta=function(a){Ta[" "](a);return a};Ta[" "]=function(){};var Ua=!Q||Q&&9<=Ka,Va=Q&&!T("9");!S||T("528");R&&T("1.9b")||Q&&T("8")||Fa&&T("9.5")||S&&T("528");R&&!T("8")||Q&&T("9");var Wa=function(a,b){this.type=a;this.target=b;p(this,this[ea]);this.defaultPrevented=this.o=!1};Wa[D].preventDefault=function(){this.defaultPrevented=!0};var X=function(a,b){Wa[G](this,a?a[A]:"");this.target=null;p(this,null);this.relatedTarget=null;this.button=this.screenY=this.screenX=this.clientY=this.clientX=this.offsetY=this.offsetX=0;q(this,0);this.charCode=0;this.metaKey=this.shiftKey=this.altKey=this.ctrlKey=!1;this.p=this.state=null;a&&this.u(a,b)};ia(X,Wa);
X[D].u=function(a,b){var c=this.type=a[A];this.target=a[ea]||a.srcElement;p(this,b);var d=a.relatedTarget;if(d){if(R){var f;t:{try{Ta(d.nodeName);f=!0;break t}catch(e){}f=!1}f||(d=null)}}else"mouseover"==c?d=a.fromElement:"mouseout"==c&&(d=a.toElement);this.relatedTarget=d;this.offsetX=S||void 0!==a.offsetX?a.offsetX:a.layerX;this.offsetY=S||void 0!==a.offsetY?a.offsetY:a.layerY;this.clientX=void 0!==a.clientX?a.clientX:a.pageX;this.clientY=void 0!==a.clientY?a.clientY:a.pageY;this.screenX=a.screenX||
0;this.screenY=a.screenY||0;this.button=a.button;q(this,a[z]||0);this.charCode=a.charCode||("keypress"==c?a[z]:0);this.ctrlKey=a.ctrlKey;this.altKey=a.altKey;this.shiftKey=a.shiftKey;this.metaKey=a.metaKey;this.state=a.state;this.p=a;a.defaultPrevented&&this[x]()};X[D].preventDefault=function(){X.t[x][G](this);var a=this.p;if(a[x])a[x]();else if(a.returnValue=!1,Va)try{(a.ctrlKey||112<=a[z]&&123>=a[z])&&q(a,-1)}catch(b){}};var Xa="closure_listenable_"+(1E6*Math.random()|0),Ya=function(a){try{return!(!a||!a[Xa])}catch(b){return!1}},Za=0;var $a=function(a,b,c,d,f,e){this.c=a;this.g=b;this.src=c;this.type=d;this.k=!!f;this.j=e;this.key=++Za;this.e=this.l=!1};$a[D].n=function(){this.e=!0;this.j=this.src=this.g=this.c=null};var ab=function(a){this.src=a;this.a={};this.m=0};ab[D].add=function(a,b,c,d,f){var e=a[B]();a=this.a[e];a||(a=this.a[e]=[],this.m++);var h;t:{for(h=0;h<a[C];++h){var m=a[h];if(!m.e&&m.c==b&&m.k==!!d&&m.j==f)break t}h=-1}-1<h?(b=a[h],c||(b.l=!1)):(b=new $a(b,null,this.src,e,!!d,f),b.l=c,a[s](b));return b};ab[D].q=function(a){var b=a[A];if(!(b in this.a))return!1;var c=this.a[b],d=wa(c,a),f;if(f=0<=d)N(null!=c[C]),O.splice[G](c,d,1);f&&(a.n(),0==this.a[b][C]&&(delete this.a[b],this.m--));return f};var bb="closure_lm_"+(1E6*Math.random()|0),cb={},db=0,gb=function(a,b,c,d,f){if("array"==K(b)){for(var e=0;e<b[C];e++)gb(a,b[e],c,d,f);return null}c=hb(c);if(Ya(a))a=a.w(b,c,d,f);else{if(!b)throw l("Invalid event type");var e=!!d,h=ib(a);h||(a[bb]=h=new ab(a));c=h.add(b,c,!1,d,f);c.g||(d=jb(),c.g=d,d.src=a,d.c=c,a.addEventListener?a.addEventListener(b[B](),d,e):a.attachEvent(kb(b[B]()),d),db++);a=c}return a},jb=function(){var a=lb,b=Ua?function(c){return a[G](b.src,b.c,c)}:function(c){c=a[G](b.src,
b.c,c);if(!c)return c};return b},kb=function(a){return a in cb?cb[a]:cb[a]="on"+a},nb=function(a,b,c,d){var f=1;if(a=ib(a))if(b=a.a[b[B]()])for(b=b.concat(),a=0;a<b[C];a++){var e=b[a];e&&e.k==c&&!e.e&&(f&=!1!==mb(e,d))}return Boolean(f)},mb=function(a,b){var c=a.c,d=a.j||a.src;if(a.l&&"number"!=typeof a&&a&&!a.e){var f=a.src;if(Ya(f))f.v(a);else{var e=a[A],h=a.g;f.removeEventListener?f.removeEventListener(e,h,a.k):f.detachEvent&&f.detachEvent(kb(e),h);db--;(e=ib(f))?(e.q(a),0==e.m&&(e.src=null,f[bb]=
null)):a.n()}}return c[G](d,b)},lb=function(a,b){if(a.e)return!0;if(!Ua){var c;if(!(c=b))t:{c=["window","event"];for(var d=J,f;f=c[t]();)if(null!=d[f])d=d[f];else{c=null;break t}c=d}f=c;c=new X(f,this);d=!0;if(!(0>f[z]||void 0!=f.returnValue)){t:{var e=!1;if(0==f[z])try{q(f,-1);break t}catch(h){e=!0}if(e||void 0==f.returnValue)f.returnValue=!0}f=[];for(e=c.currentTarget;e;e=e.parentNode)f[s](e);for(var e=a[A],m=f[C]-1;!c.o&&0<=m;m--)p(c,f[m]),d&=nb(f[m],e,!0,c);for(m=0;!c.o&&m<f[C];m++)p(c,f[m]),
d&=nb(f[m],e,!1,c)}return d}return mb(a,new X(b,this))},ib=function(a){a=a[bb];return a instanceof ab?a:null},ob="__closure_events_fn_"+(1E9*Math.random()>>>0),hb=function(a){N(a,"Listener can not be null.");if("function"==K(a))return a;N(a.handleEvent,"An object listener must have handleEvent method.");return a[ob]||(a[ob]=function(b){return a.handleEvent(b)})};var pb=function(a,b,c){t:if(c=ta(c),void 0===a[F][c]){var d=(S?"Webkit":R?"Moz":Q?"ms":Fa?"O":null)+ua(c);if(void 0!==a[F][d]){c=d;break t}}c&&(a[F][c]=b)};var qb=function(a,b){var c=[];1<arguments[C]&&(c=k[D][u][G](arguments)[u](1));var d=Na(g,"th","tct-selectall",a);if(0!=d[C]){var d=d[0],f=0,e=Na(g,"tbody",null,a);e[C]&&(f=e[0].rows[C]);this.d=Ra("input",{type:"checkbox"});d.appendChild(this.d);f?gb(this.d,"click",this.s,!1,this):r(this.d,!0);this.f=[];this.h=[];this.i=[];d=Na(g,"input",null,a);for(f=0;e=d[f];f++)"checkbox"==e[A]&&e!=this.d?(this.f[s](e),gb(e,"click",this.r,!1,this)):"action"==e[ba]&&(0<=c[y](e[w])?this.i[s](e):this.h[s](e),r(e,!0))}};
I=qb[D];I.f=null;I.b=0;I.d=null;I.h=null;I.i=null;I.s=function(a){for(var b=a[ea][da],c=a=0,d;d=this.f[c];c++)d.checked=b,a+=1;this.b=b?this.f[C]:0;for(c=0;b=this.h[c];c++)r(b,!this.b);for(c=0;b=this.i[c];c++)r(b,1!=a?!0:!1)};I.r=function(a){this.b+=a[ea][da]?1:-1;this.d.checked=this.b==this.f[C];a=0;for(var b;b=this.h[a];a++)r(b,!this.b);for(a=0;b=this.i[a];a++)r(b,1!=this.b?!0:!1)};var rb=function(){var a=U(g,"kinds");a&&new qb(a);(a=U(g,"pending_backups"))&&new qb(a);(a=U(g,"backups"))&&new qb(a,"Restore");var b=U(g,"ae-datastore-admin-filesystem");b&&gb(b,"change",function(){var a="gs"==Sa(b);U(g,"gs_bucket_tr")[F].display=a?"":"none"});if(a=U(g,"confirm_delete_form")){var c=U(g,"confirm_readonly_delete");c&&(a.onsubmit=function(){var a=U(g,"confirm_message");L("color")?pb(a,"red","color"):Aa("color",ha(pb,a));return c[da]})}},Y=["ae","Datastore","Admin","init"],Z=J;
Y[0]in Z||!Z.execScript||Z.execScript("var "+Y[0]);for(var $;Y[C]&&($=Y[t]());)Y[C]||void 0===rb?Z=Z[$]?Z[$]:Z[$]={}:Z[$]=rb;
