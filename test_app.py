import unittest
from app import ingredientes, bocadillos, pedidos, callback, ingrediente_delete, bocadillo_delete, pedido_delete, busqueda, busqueda_bocadillo, busqueda_ingrediente
class Test(unittest.TestCase):
    def test_ingredientes(self):
        self.assertEqual(ingredientes(), "Error al crear ingrediente")
    
    def test_bocadillos(self):
        self.assertEqual(bocadillos(), False)
        self.assertEqual(bocadillos(), "Error al crear bocadillos")

    def test_pedidos(self):
        self.assertEqual(pedidos(), False)
        self.assertEqual(pedidos(), "Error al crear pedido")

    def test_ingre_delete(self):
        self.assertEqual(ingrediente_delete(), "Error eliminando ingrediente")
                    
    def test_boca_delete(self):
        self.assertEqual(bocadillo_delete(), "Error eliminando bocadillo")
    
    def test_pedido_delete(self):
        self.assertEqual(pedido_delete(),"Error eliminando pedido")

    def test_pedido_delete(self):
        self.assertEqual(busqueda(),"Error al realizar la búsqueda")