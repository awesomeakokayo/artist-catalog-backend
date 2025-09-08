 const API_BASE = "http://localhost:8000"; // change to deployed url
 async function fetchCatalogs(){
    const res = await fetch(`${API_BASE}/catalogs/`);
    if(!res.ok) return console.error('failed to fetch');
    const data = await res.json();
    renderCatalogs(data);
 }
 function renderCatalogs(items){
    const grid = document.getElementById('catalog-grid');
    grid.innerHTML = '';
    items.forEach(item => {
        const card = document.createElement('article');
        card.className = 'card';
        const img = document.createElement('img');
        img.className = 'cover';
        img.src = item.cover_image ? API_BASE + item.cover_image : "/static/placeholder.png";

        img.alt = item.title;
        const h3 = document.createElement('h3');
        h3.textContent = item.title;
        const p = document.createElement('p');
        p.textContent = item.description || '';
        const links = document.createElement('div');
        links.className = 'links';
        
    if(item.spotify_url){
        const a = document.createElement('a');
        a.href = item.spotify_url; a.target = '_blank'; a.className = 'button';
        a.textContent = 'Spotify';
        links.appendChild(a);
    }
    if (item.apple_music_url) {
      const a = document.createElement("a");
      a.href = item.apple_music_url;
      a.target = "_blank";
      a.className = "button";
      a.textContent = "Apple Music";
      links.appendChild(a);
    }
    if(item.audiomack_url){
        const a = document.createElement('a');
        a.href = item.audiomack_url; a.target = '_blank'; a.className = 'button';
        a.textContent = 'Audiomack';
        links.appendChild(a);
    }
    if(item.boomplay_url){
        const a = document.createElement('a');
        a.href = item.boomplay_url; a.target = '_blank'; a.className = 'button';
        a.textContent = 'Boomplay';
        links.appendChild(a);
    }
    if(item.youtubemusic_url){
        const a = document.createElement('a');
        a.href = item.youtubemusic_url; a.target = '_blank'; a.className = 'button';
        a.textContent = 'YouTube Music';
        links.appendChild(a);
    }
    card.appendChild(img);
    card.appendChild(h3);
    card.appendChild(p);
    card.appendChild(links);
    grid.appendChild(card);
 });
 }
 // Boot
 fetchCatalogs();