
const urlsToCache = ["/", "style.css", "offline.html", "logos/logo_162.png"];
self.addEventListener("install", event => {
	event.waitUntil(
	   caches.open("pwa-assets")
	   .then(cache => {
		  return cache.addAll(urlsToCache);
	   })
	);
 });

 self.addEventListener("activate", event => {
	console.log("Service worker activated");
 });

 self.addEventListener("fetch", event => {
	event.respondWith(
	  fetch(event.request)
	  .catch(error => {
		console.log(caches.match(event.request))
		if (!caches.match(event.request)) {
			return caches.match(event.request)
		} else {return caches.match("offline.html")}
	  })
	);
 });