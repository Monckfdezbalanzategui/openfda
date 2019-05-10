import json
import http.server
import http.client
import socketserver

#En primer lugar vamos a definir la información en la que va  basar el servidor web

PUERTO=8000
URL_API_openfda="api.fda.gov"
#Creamos la interfaz html en un documento a parte por comodidad
HTML="DOC.html"
HTML_404="HTML_4"
NOMBRE_SRC="/drug/label.json"
mensaje_html="mensaje_html.html"
header={"User-Agent":"http-client"}
socketserver.TCPServer.allow_reuse_address=True


# clase que hereda los métodos del handler http (usado para implementar servidores web)

class TestHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def act_openfda (self,busqueda="",limit=1):
        peticion = "{}?limit={}".format(NOMBRE_SRC,limit)
        #Si queremos un segundo parámetro, para buscar medicamento o empresas:
        if busqueda != "":
            peticion += "&{}".format(busqueda)

        print("Ha solicitado el siguiente recurso: {}".format(peticion))

        #Establecemos  conexión

        conexion=http.client.HTTPSConnection(URL_API_openfda)

        #Qué solicitamos de la conexión?

        conexion.request("GET",peticion,None,header)

        #Finalmente, nos llega la respuesta

        respuesta = conexion.getresponse()

        if respuesta.status == 404:
            with open (HTML_404, "r") as er:
                error=er.read()
                exit(1)
            return error

        else:
            print("Estado de la página= {}".format(respuesta.status,respuesta.reason))

        # Debemos tener en cuenta que la página puede haber quedado obsoleta o no ser accesible, es decir,
        # el status nos devuelva el famoso error 404

        #Leemos ahora nuestra respuesat con json

        med_json=respuesta.read().decode("utf-8")
        conexion.close()

        return json.loads(med_json)

    def interfaz_html(self):

        with open (HTML, "r") as h:
            interfaz=h.read()

        return interfaz
    def list_drugs(self,limit=10):

        medicamentos=self.act_openfda(limit)

        #obtenemos la lista d emedicamentos con la inofrmación:

        mensaje=(""""<!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                    </head>
                    <body>
                   <p>Nombre medicamento. Marca. Fabricante. Id. Propósito</p>
                   <ul>""")



        for medicamento in medicamentos["results"]:

            id_med = medicamento["id"]

            try:
                accion= medicamento["porpouse"][0]
            except KeyError:
                accion="Desconocido"

            if medicamento["openfda"]:
                nombre_med=medicamento["openfda"]["substance_name"][0]
                marca_med=medicamento["openda"]["brand_name"][0]
                fabricante_med=medicamento["openfda"]["manufacturer_name"][0]
            else:
                nombre_med = "Desconocido"
                marca_med = "Desconocido"
                fabricante_med = "Desconocido"

            mensaje += ("<li>{}. {}. {}. {}. {}.</li>".format(nombre_med,marca_med,fabricante_med,id_med,accion))

        mensaje += ("""</ul>
                    <a href="/">Home</a>
                    </body>
                    </html>""")
        return mensaje

    def searchDrug (self,sustancia_activa,limit=20):


        medicamentos=self.act_openfda("searchDrug",limit)

        mensaje=("""<!DOCTYPE html>
                   html lang="es">
                   head>
                       <meta charset="UTF-8">
                   </head>
                   <body>
                   <p>Medicamento buscado</p>
                   
                   <ul>""")
        for medicamento in medicamentos["results"]:
            if medicamento["open_fda"]:
                if medicamento["openfda"]["generic_name"][0] == sustancia_activa:
                    medicamento_buscado=medicamento

                    mensaje += "<li> {} </li>".format(medicamento_buscado)

        mensaje += ("""</ul>
                    <a href="/">Home</a>
                    </body>
                    </html>""")
        return mensaje
    def list_companies(self, limit=20):

        medicamentos = self.act_openfda(limit)

        mensaje =("""<!DOCTYPE html>
                   html lang="es">
                   head>
                       <meta charset="UTF-8">
                   </head>
                   <body>
                   <p>Fabricantes</p>
                   
                   <ul>""")
        for medicamento in medicamentos["results"]:
            if medicamento["openfda"]:
                try:
                    mensaje += ("<li> {} </li>".format(medicamento["openfda"]["manufacturer_name"][0]))
                except KeyError:
                    pass

        mensaje += ("""</ul>
                    <a href="/">Home</a>
                    </body>
                    </html>""")
        return mensaje

    def searchCompany(self,nombre,limit=20):

        medicamentos = self.act_openfda("searchCompany",limit)

        mensaje = ("""<!DOCTYPE html>
                           html lang="es">
                           head>
                               <meta charset="UTF-8">
                           </head>
                           <body>
                           <p>Empresas</p>

                           <ul>""")
        for medicamento in medicamentos["results"]:
            if medicamento["openfda"]:
                if medicamento["openfda"]["manufacturer_name"][0] == nombre:
                    empresa = medicamento

                    mensaje += "<li> {} </li> ". format(empresa)
        mensaje += ("""</ul>
                    <a href="/">Home</a>
                    </body>
                    </html>""")
        return mensaje

    def listWarnings(self,limit):

        medicamentos= self.act_openfda(limit)

        mensaje = (""""<!DOCTYPE html>
                           <html lang="es">
                           <head>
                               <meta charset="UTF-8">
                           </head>
                           <body>
                          <p>Warnings</p>
                          <ul>""")
        for medicamento in medicamentos["results"]:
            if medicamento["warnings"]:
                warnings=medicamento["warnings"][0]

                try:
                    mensaje += "<li> {} </li> ". format(warnings)
                except KeyError:
                    pass
    def do_GET(self):

        mensaje=""

        lista_recursos=self.path.split("?")
        final=lista_recursos[0]
        if len(lista_recursos)>1:
            params=lista_recursos[1]

        if params:
            params.split("=",1)
            if params [0] == "limit":
                limit=int(params[1])
            else:
                limit=1

            if "&" in params:
                params=params.split("&")
                params2=params.split("=")

                if params2[0]=="searchDrug":
                    sustancia_activa=params2[1]
                    mensaje=self.searchDrug(sustancia_activa,limit)

                elif params2[0]=="searchCompany":
                    nombre=params2[1]
                    mensaje=self.searchCompany(nombre,limit)


        if final =="/":

            mensaje= self.interfaz_html()

        elif final == "/listDrugs":

            mensaje= self.list_drugs(limit)

        elif final == "/listCompanies":

            mensaje= self.list_companies(limit)

        elif "warnings" in self.path:
            mensaje= self.listWarnings(limit)

        elif "secret" in self.path:
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=""Mi servidor""")
            self.end_headers()

        elif "redirect" in self.path:
            print('Mandamos la redireccion a la página principal')
            self.send_response(301)
            self.send_header('Location', 'http://localhost:' + str(PUERTO))
            self.end_headers()



        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(mensaje, "utf8"))



        return

Handler = TestHTTPRequestHandler

httpd = socketserver.TCPServer(("", PUERTO), Handler)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("Interrumpido por el usuario")

print("")
print("Se ha finalizado el servicio")
