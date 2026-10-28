"""Build a dependency-free GitHub Pages website from editable HTML fragments."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape
import json, re, posixpath, sys

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT / 'site'
CONTENT = ROOT / 'content'
CONTENT.mkdir(exist_ok=True)
CONTACT = 'screed@rosesantiques.com'
DOMAIN = 'www.nrauctiongallery.com'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
DEPARTMENTS = {'l101':'Paintings','l114':'Furniture & Silver','l126':'Furniture & Silver','l140':'Asian Art','l205':'Decorative Arts','l212':'Asian Art','l030':'Paintings','l045':'Furniture & Silver','l052':'Asian Art'}

class Rewrite(HTMLParser):
    def __init__(self, route):
        super().__init__(convert_charrefs=True)
        self.route = route
        self.output = []
    def relative(self, path):
        target = path.strip('/')
        if not target.startswith('assets/'):
            target = target + '/index.html' if target else 'index.html'
        return posixpath.relpath(target, self.route.strip('/') or '.')
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        a.pop('data-status', None)
        for key in ('href','src'):
            if a.get(key,'').startswith('/'):
                original = a[key]
                if tag == 'a' and original.startswith('/lots/'):
                    a['data-department'] = DEPARTMENTS.get(original.rsplit('/',1)[-1], '')
                    a['data-lot'] = original.rsplit('/',1)[-1].lstrip('l0')
                a[key] = self.relative(original)
        if tag in ('input','textarea') and a.get('placeholder'):
            a['aria-label'] = a['placeholder']
            if a.get('name') in ('name','email','phone'):
                a['autocomplete'] = {'name':'name','email':'email','phone':'tel'}[a['name']]
        if tag == 'button' and a.get('aria-pressed') is not None:
            a['type'] = 'button'
            a['data-language'] = 'en' if a['aria-pressed']=='true' else 'zh'
        if tag == 'main':
            a['id'] = 'main-content'
        if tag == 'form':
            a['data-inquiry'] = 'valuation' if self.route == '/sell' else 'bid'
        self.output.append('<'+tag+''.join(' '+k if v is None else ' '+k+'="'+escape(v,quote=True)+'"' for k,v in a.items())+'>')
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
    def handle_endtag(self, tag):
        if tag not in VOID: self.output.append('</'+tag+'>')
    def handle_data(self, data): self.output.append(escape(data,quote=False))
    def handle_comment(self, data):
        if data == ' ': self.output.append('<!-- -->')

pages_file = CONTENT / 'pages.json'
if not pages_file.exists():
    pages = json.loads((ROOT/'reference/pages.json').read_text())
    for route, name in pages.items():
        raw=(ROOT/'reference'/name).read_text()
        title=unescape(re.search(r'<title>(.*?)</title>',raw).group(1))
        fragments=[]
        for tag in ('header','main','footer'):
            fragments.append(re.search('<'+tag+r'\b[\s\S]*?</'+tag+'>',raw).group(0))
        (CONTENT/name).write_text('\n'.join(fragments))
        pages[route]={'file':name,'title':title}
    pages_file.write_text(json.dumps(pages,indent=2,ensure_ascii=False))
else:
    pages=json.loads(pages_file.read_text())

if not (SITE/'assets/translations.json').exists():
    source=(ROOT/'reference/language.js').read_text().split('m={',1)[1].split('},h=f()',1)[0]
    translations={a or b:c for a,b,c in re.findall(r'(?:"([^"]+)"|(\w+)):`([^`]*)`',source)}
    translations.update({
      'Prepare valuation email':'准备估价邮件','Prepare bid email':'准备竞投邮件',
      'Your email app will open with your inquiry. Please send the email to complete your request.':'您的邮件应用将打开并填入咨询内容。请发送邮件以完成申请。',
      'Bids are subject to confirmation by our bids office.':'竞投须经我们的竞投部门确认。',
      'Contact our specialists':'联系我们的专家', 'Skip to content':'跳至正文',
      'Email draft prepared. Please send it from your email app. Nothing has been submitted yet.':'邮件草稿已准备好。请在邮件应用中发送。目前尚未提交任何内容。',
      'If your email app did not open, email us directly:':'如果邮件应用未打开，请直接发送邮件至：',
      'Copy inquiry':'复制咨询内容', 'Inquiry copied. Paste it into an email to':'咨询内容已复制。请粘贴到邮件并发送至',
      'No lots match your search.':'没有符合条件的拍品。',
      'Page not found':'页面未找到', 'Return to the gallery':'返回首页',
      'This page may have moved. Explore our upcoming auctions or return to the homepage.':'此页面可能已移动。请浏览即将举行的拍卖或返回首页。'
    })
    (SITE/'assets/translations.json').write_text(json.dumps(translations,ensure_ascii=False,indent=2))

for route,info in pages.items():
    fragment=(CONTENT/info['file']).read_text()
    fragment=re.sub(r'<script\b[\s\S]*?</script>','',fragment)
    fragment=fragment.replace('Submit for valuation','Prepare valuation email').replace('Submit bid','Prepare bid email')
    if '<form' in fragment:
        note='<p class="inquiry-note text-sm text-muted-foreground">Your email app will open with your inquiry. Please send the email to complete your request.</p>'
        if route.startswith('/lots/'):
            note+='<p class="inquiry-note text-sm text-muted-foreground">Bids are subject to confirmation by our bids office.</p>'
            estimate=re.search(r'Estimate.*?\$([\d,]+)',fragment)
            if estimate: fragment=fragment.replace('min="1"','min="'+estimate.group(1).replace(',','')+'"')
        fragment=fragment.replace('</form>',note+'<p class="form-status" role="status" aria-live="polite" hidden></p></form>')
    fragment=fragment.replace('</footer>',f'<p class="mt-4"><a class="contact-link" href="mailto:{CONTACT}">{CONTACT}</a></p><address class="mailing-address"><span>Mailing address</span><br>PO Box 59041<br>Rockville, MD 20859</address></footer>')
    rw=Rewrite(route); rw.feed(fragment)
    body=''.join(rw.output)
    asset=posixpath.relpath('assets',route.strip('/') or '.')
    canonical='https://'+DOMAIN+('/' if route=='/' else route+'/')
    title=escape(info['title'])
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="Discover fine art, antiques, silver and Asian works of art at N&amp;R Auction Gallery. Browse auctions and request a complimentary valuation.">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{title}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://{DOMAIN}/assets/hero-gallery-DVq41kwE.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{asset}/favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Karla:wght@400;500;600&amp;display=swap">
<link rel="stylesheet" href="{asset}/styles.css"><link rel="stylesheet" href="{asset}/enhancements.css"><script defer src="{asset}/app.js"></script></head>
<body data-contact="{CONTACT}"><a class="skip-link" href="#main-content">Skip to content</a>{body}</body></html>'''
    target=SITE/route.strip('/')/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(html)

(SITE/'.nojekyll').write_text('')
(SITE/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n')
(SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://'+DOMAIN+('/' if route=='/' else route+'/')+'</loc></url>' for route in pages)+'</urlset>')
print(f'Built {len(pages)} pages in {SITE}')
