from django.shortcuts import render,redirect
from django.views import View
from cliente import models as cliente_models
from administrador import models as admin_models
# Create your views here.



import io
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet






def get_Compras(user):
    try:
        compras=list(cliente_models.Compra.objects.all().order_by('-id'))
        contexto=[]
        if compras.__len__() > 0:
            for cc in compras:
                detalles=list(cliente_models.Detalle.objects.filter(compraid=cc))
                dd=[]
                total=0
                for dt in detalles:
                    total+=dt.cantidad*dt.productoid.precio
                
                for d in detalles:
                    dd.append({"detalle":d,"subtotal":d.cantidad*d.productoid.precio})
                if dd.__len__()==0:
                    dd=None
                contexto.append({"compra":cc,"detalles":dd,"total":total})
            if contexto.__len__()>0:
                return contexto
            return None
    except Exception as e:
        print(e)
    return None


















class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"Dependiente/home.html")
        return redirect("../../../../../../../admin/")


class Ventas(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"Dependiente/ventas.html",{
                "compras":get_Compras(request.user)
            })
        return render("../../../../../../../../../../admin/")
    
class Hacer_Entrega(View):
    def get(self,request,ventaid):
        if request.user.is_authenticated:
            try:
                compra=cliente_models.Compra.objects.get(id=ventaid)
                compra.pendiente=False
                compra.save()
                return redirect("../../../../../../../../../dependiente/ventas/")
            except Exception as e:
                print(e)
        return render("../../../../../../../../../../admin/")
    

def generar_reporte_ventas(request):
    if request.user.is_authenticated:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Obtén todas las ventas realizadas
        ventas = cliente_models.Compra.objects.all()

        # Estilo para las etiquetas
        styles = getSampleStyleSheet()

        # Crea una lista de elementos para el contenido del PDF
        flowables = []

        for venta in ventas:
            detalles = cliente_models.Detalle.objects.filter(compraid=venta)
            rows = [["Producto", "Cantidad", "Precio", "Subtotal"]]

            total_general = 0

            for detalle in detalles:
                subtotal = detalle.productoid.precio * detalle.cantidad
                rows.append([detalle.productoid.nombre, detalle.cantidad, detalle.productoid.precio, subtotal])
                total_general += subtotal

            # Agrega el total general al final de la tabla
            rows.append(["", "", "Total General:", total_general])

            table = Table(rows)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]))

            # Agrega la fecha de la venta como etiqueta
            etiqueta_fecha = Paragraph(f"Venta realizada el {venta.fecha}", styles["Heading1"])
            flowables.append(etiqueta_fecha)
            flowables.append(table)

        # Construye el documento con los elementos
        doc.build(flowables)

        # Devuelve el PDF como una respuesta de archivo adjunto
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="reporte_ventas.pdf")
    else:
        return redirect("../../../../admin/")