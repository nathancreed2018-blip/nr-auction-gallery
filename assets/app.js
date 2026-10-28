(() => {
  'use strict';
  const scriptUrl = document.currentScript.src;
  const contact = document.body.dataset.contact;
  const textNodes = [], attributes = [];
  let language = 'en', translations = {};
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    if (node.textContent.trim() && !['SCRIPT','STYLE'].includes(node.parentElement.tagName)) textNodes.push([node,node.textContent]);
  }
  document.querySelectorAll('[placeholder],[aria-label],img[alt]').forEach(el => {
    ['placeholder','aria-label','alt'].forEach(attr => { if(el.hasAttribute(attr)) attributes.push([el,attr,el.getAttribute(attr)]); });
  });
  const t = value => language === 'zh' ? translations[value] || value : value;
  const translate = value => value.replace(/^(\s*)(.*?)(\s*)$/s, (_,a,b,c) => a+t(b)+c);
  function setLanguage(next) {
    language = next;
    document.documentElement.lang = next === 'zh' ? 'zh-CN' : 'en';
    textNodes.forEach(([el,value]) => {el.textContent=translate(value);});
    attributes.forEach(([el,attr,value]) => el.setAttribute(attr,t(value)));
    document.querySelectorAll('[data-language]').forEach(button => {
      const active=button.dataset.language===next;
      button.setAttribute('aria-pressed',String(active));
      button.classList.toggle('font-semibold',active);
      button.classList.toggle('text-muted-foreground',!active);
    });
    try {localStorage.setItem('nr-language',next);} catch {}
    filterLots();
  }
  document.querySelectorAll('[data-language]').forEach(button => button.addEventListener('click',()=>setLanguage(button.dataset.language)));
  fetch(new URL('translations.json',scriptUrl)).then(response=>response.json()).then(data=> {
    translations=data;
    let saved='en';try {saved=localStorage.getItem('nr-language')||'en';} catch {}
    setLanguage(saved==='zh'?'zh':'en');
  }).catch(()=>{});

  const search=document.querySelector('input[placeholder="Search by title, maker or lot number"]');
  const department=search?.parentElement.querySelector('select');
  const cards=search ? [...document.querySelectorAll('main a[data-lot]')] : [];
  cards.forEach(card=>card.dataset.search=card.textContent.toLowerCase());
  let empty;
  if(search) {
    search.type='search';
    search.setAttribute('aria-label','Search by title, maker or lot number');
    empty=document.createElement('p');empty.className='mt-10 text-muted-foreground';empty.setAttribute('role','status');empty.hidden=true;
    cards[0]?.parentElement.after(empty);
    search.addEventListener('input',filterLots);
    department.addEventListener('change',filterLots);
  }
  function filterLots() {
    if(!search)return;
    const query=search.value.trim().toLowerCase();let count=0;
    cards.forEach(card=>{
      const found=(!department.value||card.dataset.department===department.value)&&(!query||(card.dataset.search+' '+card.textContent.toLowerCase()).includes(query));
      card.hidden=!found;if(found)count++;
    });
    empty.hidden=count>0;empty.textContent=t('No lots match your search.');
  }
  document.querySelectorAll('form[data-inquiry]').forEach(form=> {
    form.addEventListener('submit',event=> {
      event.preventDefault();
      if(!form.reportValidity())return;
      const data=new FormData(form),bid=form.dataset.inquiry==='bid';
      const title=document.querySelector('h1').textContent;
      const subject=bid ? 'Absentee bid inquiry — '+title : 'Valuation request — N&R Auction Gallery';
      const lines=['N&R Auction Gallery',subject,''];
      for(const [key,value] of data) if(String(value).trim()) lines.push(key.charAt(0).toUpperCase()+key.slice(1)+': '+String(value).trim());
      lines.push('','Page: '+location.href);
      if(bid)lines.push('Please confirm receipt and acceptance of this bid.');
      const body=lines.join('\n');
      const href='mailto:'+contact+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
      const status=form.querySelector('.form-status');
      status.hidden=false;status.replaceChildren();
      const message=document.createElement('span');message.textContent=t('Email draft prepared. Please send it from your email app. Nothing has been submitted yet.')+' ';
      const link=document.createElement('a');link.href=href;link.textContent=contact;
      const copy=document.createElement('button');copy.type='button';copy.className='copy-inquiry';copy.textContent=t('Copy inquiry');
      copy.addEventListener('click',async()=>{
        try {await navigator.clipboard.writeText(body);message.textContent=t('Inquiry copied. Paste it into an email to')+' ';} catch {message.textContent=body;}
      });
      status.append(message,link,copy);
      location.href=href;
    });
  });
})();
