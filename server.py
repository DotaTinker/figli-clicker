from http.server import HTTPServer, CGIHTTPRequestHandler

server_adres = ("", 8080)
httpd = HTTPServer(server_adres, CGIHTTPRequestHandler)
httpd.serve_forever()
