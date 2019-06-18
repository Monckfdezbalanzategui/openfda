import socketserver
import http.server
import http.client
import json

PORT = 8000

#Clase con  manejador. Es una clase derivada de BaseHTTPRequestHandler
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    #parámetros
    SERVER_NAME = "api.fda.gov" #de dónde obtenemos la info
    RESOURCE_NAME = "/drug/label.json" #path más sencillo
    DRUG= '&search=active_ingredient:' #path con parámetro
    COMPANY = '&search=openfda.manufacturer_name:'


    def lectura(self):

        f=open("formulario.html", "r") #Abrimos y leemos el formulario
        message=f.read()

        return message


    #Con esta función almacenamos los datos en forma html
    def input_html(self, lista):

        datos_html = """ """

        for i in lista:
            datos_html += "<li>" + i + "</li>"
        datos_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return datos_html


    #Conectamos con openfda y almacenamos resultados
    def resultados(self, limit=10):

        conn = http.client.HTTPSConnection(self.SERVER_NAME)
        conn.request("GET", self.RESOURCE_NAME + "?limit=" + str(limit))

        print(self.RESOURCE_NAME + "?limit=" + str(limit))


        r1 = conn.getresponse()
        leer_json = r1.read().decode("utf8")
        data = json.loads(leer_json)

        results = data['results']


        return results


# GET. Este metodo se invoca automaticamente cada vez que hay una
# peticion GET por HTTP. El rescurso lo hemos definido antes ne los paths
    def do_GET(self):

        #A partir de ? están los parámetro con lo que:
        division_lista = self.path.split("?")


        if len(division_lista) > 1:
            parametros = division_lista[1]

        else:
            parametros = ""

        #Valor por defecto (el más sencillo)
        limit = 1


        if parametros:

            print ("Hay parametros")
            division_parametro = parametros.split("=")

            if division_parametro[0] == "limit":
                limit = int(division_parametro[1])
                print("Limit: {}".format(limit))

        else:

            print("No hay parámetros")




        if self.path == '/':

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            formulario_html = self.lectura()
            self.wfile.write(bytes(formulario_html, "utf8"))


        elif 'listDrugs' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            drugs = []
            results = self.resultados(limit)

            for resultado in results:

                if ('generic_name' in resultado['openfda']):
                    drugs.append(resultado['openfda']['generic_name'][0])

                else:
                    drugs.append('Desconocido')


            html_devuelve = self.input_html(drugs)


            self.wfile.write(bytes(html_devuelve, "utf8"))



        elif 'listCompanies' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            empresas = []
            results = self.resultados(limit)

            for resultado in results:

                if ('manufacturer_name' in resultado['openfda']):
                    empresas.append(resultado['openfda']['manufacturer_name'][0])

                else:
                    empresas.append('Desconocido')


            html_devuelve = self.input_html(empresas)


            self.wfile.write(bytes(html_devuelve, "utf8"))



        elif 'searchDrug' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


            limit = 10


            farmaco = self.path.split('=')[1]

            medicamentos = []

            conn = http.client.HTTPSConnection(self.SERVER_NAME)
            conn.request("GET", self.RESOURCE_NAME + "?limit=" + str(limit) + self.DRUG + farmaco)

            r1 = conn.getresponse()
            leer1 = r1.read()
            dato = leer1.decode("utf8")
            datos_json = json.loads(dato)
            events_search_drug = datos_json['results']

            for resultado in events_search_drug:
                if ('generic_name' in resultado['openfda']):
                    medicamentos.append(resultado['openfda']['generic_name'][0])
                else:
                    medicamentos.append('Desconocido')


            html_devuelve = self.input_html(medicamentos)


            self.wfile.write(bytes(html_devuelve, "utf8"))




        elif 'searchCompany' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


            limit = 10


            empresa = self.path.split('=')[1]

            empresas = []
            conn = http.client.HTTPSConnection(self.SERVER_NAME)
            conn.request("GET", self.RESOURCE_NAME + "?limit=" + str(limit) + self.COMPANY+ empresa)

            r1 = conn.getresponse()
            leer1 = r1.read()
            dato = leer1.decode("utf8")
            datos_json = json.loads(dato)
            event_findempresa = datos_json['results']

            for search in event_findempresa:
                empresas.append(search['openfda']['manufacturer_name'][0])


            html_devuelve = self.input_html(empresas)


            self.wfile.write(bytes(html_devuelve, "utf8"))



        elif 'listWarnings' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            warnings = []
            results = self.resultados(limit)

            for resultado in results:

                if ('warnings' in resultado):
                    warnings.append(resultado['warnings'][0])

                else:
                    warnings.append('Desconocido')


            html_devuelve = self.input_html(warnings)


            self.wfile.write(bytes(html_devuelve, "utf8"))




        elif 'redirect' in self.path:
            print('Volvemos a la pagina principal')
            self.send_response(301)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()

        elif 'secret' in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()

        else:
            print ("El recurso solicitado no se encuentra en el servidor")
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("ERROR 404, NOT FOUND '{}'.".format(self.path).encode())
        return

socketserver.TCPServer.allow_reuse_address = True  # reutilizamos el puerto
Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)

httpd.serve_forever()
