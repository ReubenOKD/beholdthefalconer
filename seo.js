var SITE="https://beholdthefalconer.com";
function seoSect(c){return {metaphysics:'Metaphysics & Meaning',power:'Power & Persuasion',media:'Media & Myth'}[c]||c;}

function seoAttr(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function seoText(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function seoPlain(h){return String(h).replace(/<[^>]+>/g,' ').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/\s+/g,' ').trim();}

function seoDesc(p){var d=seoPlain(p.excerpt||p.body);return d.length>158?d.slice(0,155).replace(/\s+\S*$/,'')+'...':d;}

function buildArticlePage(p,posts,cover){
  var url=SITE+'/'+p.slug, d=seoDesc(p), img=SITE+'/'+(cover||'falconer.jpg');
  var ld={'@context':'https://schema.org','@type':'Article',headline:p.title,description:d,datePublished:p.date,dateModified:p.date,image:img,mainEntityOfPage:url,articleSection:seoSect(p.cat),author:{'@type':'Person',name:'The Falconer'},publisher:{'@type':'Organization',name:'Behold the Falconer',url:SITE+'/'}};
  var more=posts.filter(function(q){return q.slug!==p.slug;}).sort(function(a,b){return a.date<b.date?1:-1;}).slice(0,8).map(function(q){return '<li><a href="/'+seoAttr(q.slug)+'">'+seoText(q.title)+'</a></li>';}).join('');
  var dt=new Date(p.date+'T00:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'});
  return '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
  +'<title>'+seoText(p.title)+' | Behold the Falconer</title>\n'
  +'<meta name="description" content="'+seoAttr(d)+'">\n'
  +'<link rel="canonical" href="'+url+'">\n'
  +'<meta property="og:type" content="article">\n<meta property="og:site_name" content="Behold the Falconer">\n'
  +'<meta property="og:title" content="'+seoAttr(p.title)+'">\n<meta property="og:description" content="'+seoAttr(d)+'">\n<meta property="og:url" content="'+url+'">\n<meta property="og:image" content="'+img+'">\n'
  +'<meta property="article:published_time" content="'+p.date+'">\n<meta property="article:section" content="'+seoAttr(seoSect(p.cat))+'">\n'
  +'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="'+seoAttr(p.title)+'">\n<meta name="twitter:description" content="'+seoAttr(d)+'">\n<meta name="twitter:image" content="'+img+'">\n'
  +'<link rel="icon" href="/falconer-sm.jpg">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
  +'<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">\n'
  +'<link rel="stylesheet" href="/article.css">\n'
  +'<script type="application/ld+json">'+JSON.stringify(ld).replace(/</g,'\\u'+'003c')+'</script>\n</head>\n<body>\n'
  +'<header class="bar"><a class="brand" href="/">Behold the <span>Falconer</span></a><nav><a href="/#metaphysics">Metaphysics &amp; Meaning</a><a href="/#power">Power &amp; Persuasion</a><a href="/#media">Media &amp; Myth</a><a href="/#aphorisms">Aphorisms</a><a href="/#archive">Archives</a></nav></header>\n'
  +'<main class="article">\n<div class="crumbs"><a href="/">Home</a> &rsaquo; <a href="/#'+seoAttr(p.cat)+'">'+seoText(seoSect(p.cat))+'</a></div>\n'
  +'<h1>'+seoText(p.title)+'</h1>\n<div class="by">By The Falconer &middot; <time datetime="'+p.date+'">'+dt+'</time></div>\n'
  +(cover?'<img class="cover" src="/'+seoAttr(cover)+'" alt="'+seoAttr(p.title)+'">\n':'')
  +'<div class="body">'+p.body+'</div>\n'
  +'<section class="more"><h2>More from the journal</h2><ul>'+more+'</ul><p><a class="btn" href="/#archive">All writings</a></p></section>\n</main>\n'
  +'<footer><div>Behold the Falconer &mdash; an independent journal of philosophy and theology.</div><div><a href="/">Home</a> &middot; <a href="/#about">About</a> &middot; <a href="/#software">Software</a> &middot; <a href="/#support">Support</a></div></footer>\n</body>\n</html>\n';
}

function buildSitemap(posts){
  var u=[{loc:SITE+'/',lm:posts.map(function(p){return p.date;}).sort().pop(),pr:'1.0'}];
  posts.slice().sort(function(a,b){return a.date<b.date?1:-1;}).forEach(function(p){u.push({loc:SITE+'/'+p.slug,lm:p.date,pr:'0.8'});});
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+u.map(function(x){return '<url><loc>'+x.loc+'</loc><lastmod>'+x.lm+'</lastmod><priority>'+x.pr+'</priority></url>';}).join('\n')+'\n</urlset>\n';
}
