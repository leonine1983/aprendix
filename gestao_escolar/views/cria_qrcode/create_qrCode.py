from django.shortcuts import render
#from qr_code.qrcode.utils import QRCodeOptions



def Create_QrCode(request):
    # Contexto usado para renderizar o QrCode
    context = dict(   
        conteudo_page = 'QR_code',
        titulo_page = "Criar QRcode"


        
    )

    



    
    return render(request, 'Escola/inicio.html', context=context)



