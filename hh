{
  "$schema": "https://json.schemastore.org/staticwebapp.config.json",
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": [
      "/api/*",
      "*.{png,jpg,jpeg,gif,svg,webp,pdf,css,js,ico,woff,woff2,ttf,eot,map}"
    ]
  },
  "mimeTypes": {
    ".json": "application/json"
  },
  "globalHeaders": {
    "X-Content-Type-Options": "nosniff"
  }
}
