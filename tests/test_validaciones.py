import unittest
from datetime import datetime, timedelta
from api_club.validators.reservas import validar_creacion, TZ
from api_club.validators.socios import validar_alta_socio

class ValidacionesTest(unittest.TestCase):
    def test_email_se_normaliza(self):
        r=validar_alta_socio({'nombre':' Ana ','email':' ANA@EXAMPLE.COM '})
        self.assertEqual(r['email'],'ana@example.com')
    def test_reserva_consecutiva_modela_intervalo_valido(self):
        d=(datetime.now(TZ)+timedelta(days=10)).replace(hour=18,minute=0,second=0,microsecond=0)
        f=d+timedelta(hours=2)
        data={'id_socio':1,'id_cancha':1,'fecha_hora_inicio':d.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00'),'fecha_hora_fin':f.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00')}
        *_,horas=validar_creacion(data);self.assertEqual(horas,2)
    def test_rechaza_mas_de_tres_horas(self):
        d=(datetime.now(TZ)+timedelta(days=10)).replace(hour=10,minute=0,second=0,microsecond=0);f=d+timedelta(hours=4)
        data={'id_socio':1,'id_cancha':1,'fecha_hora_inicio':d.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00'),'fecha_hora_fin':f.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00')}
        with self.assertRaises(ValueError):validar_creacion(data)
if __name__=='__main__':unittest.main()
