import http.server
import socketserver
import os
import webbrowser

PORT = 8006
target_dir = os.path.abspath(os.path.join('src', 'main', 'xiaozhi-server', 'test'))
os.chdir(target_dir)

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    webbrowser.open(f'http://localhost:{PORT}/test_page.html')
    print(f"服务端已启动，在：http://localhost:{PORT}，请在浏览器中打开")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        print("\n服务端已停止")
