import unittest
from app import ingredientes, bocadillos, pedidos, callback, ingre_delete, boca_delete, pedido_delete
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
        self.assertEqual(ingre_delete(), "Error eliminando ingrediente")
                    
    def test_boca_delete(self):
        self.assertEqual(boca_delete(), "Error eliminando bocadillo")
    
    def test_pedido_delete(self):
        self.assertEqual(pedido_delete(),"Error eliminando pedido")