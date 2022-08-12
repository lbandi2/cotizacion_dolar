from definitions import ARSBNA, ARSBBVA, ARSSantander, ARSPatagonia, ARSDolarBlue, COP

URL_BNA = "https://www.bna.com.ar/Personas"
URL_BBVA = "https://diariodolar.com/cotizacion-dolar-banco-frances"
URL_SANTANDER = "https://banco.santanderrio.com.ar/exec/cotizacion/index.jsp"
URL_PATAGONIA = "https://ebankpersonas.bancopatagonia.com.ar/eBanking/usuarios/cotizacionMonedaExtranjera.htm"
URL_BLUE = "https://dolarhoy.com"
URL_COP = "https://www.dolarhoy.co"

TARJETA_COMISSION = 1.65

ARSBNA(URL_BNA, TARJETA_COMISSION)
ARSBBVA(URL_BBVA, TARJETA_COMISSION)
ARSSantander(URL_SANTANDER, TARJETA_COMISSION)
ARSPatagonia(URL_PATAGONIA, TARJETA_COMISSION)
ARSDolarBlue(URL_BLUE)
COP(URL_COP)
