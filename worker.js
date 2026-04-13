export default {
  async fetch(req) {
    const lat = req.cf?.latitude;
    const lon = req.cf?.longitude;
    
    let html = await fetch('https://raw.githubusercontent.com/aahspaghetticode/clowds.py/main/index.html').then(r => r.text());
    
    // inject coords before </body>
    html = html.replace('</body>', `<script>window._cfLat=${lat};window._cfLon=${lon};</script></body>`);
    
    return new Response(html, { headers: { 'Content-Type': 'text/html' }});
  }
}
