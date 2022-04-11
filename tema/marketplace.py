"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
import logging
import unittest
from logging.handlers import RotatingFileHandler
from threading import Lock, currentThread
from tema.product import Tea, Coffee


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    logger = logging.getLogger('marketplace.log')
    # creez fisierul de log
    handler = RotatingFileHandler("marketplace.log", maxBytes=20000, backupCount=10)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    handler.setFormatter(formatter)
    # setez timpul global
    logging.Formatter.converter = time.gmtime
    logger.addHandler(handler)

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        # key = producer_id, value = nr products in queue
        self.producers_queue_len = {}
        # list of lists [id_producer, product] - available products
        self.stock_products = []
        # key - id_cart, val - list of lists [id_producer, product]
        self.list_of_carts = {}
        self.queue_size_per_producer = queue_size_per_producer
        # Producers lock
        self.producers_id_lock = Lock()
        # Consumers locks
        self.cart_id_lock = Lock()
        self.place_order_lock = Lock()
        self.stock_products_lock = Lock()




    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # returnez id-ul producer-ului
        with self.producers_id_lock:
            self.logger.info("Starting  register_producer")
            self.producers_queue_len[len(self.producers_queue_len)] = 0
            self.logger.info("Finished  register_producer")
        return len(self.producers_queue_len) - 1

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """


        self.logger.info("Starting  publish product %s by prod id %d", product, producer_id)
        if self.producers_queue_len[producer_id] < self.queue_size_per_producer:
            # adaug produsul in lista de produse si incrementez nr de produse publicate.
            self.producers_queue_len[producer_id] += 1
            self.stock_products.append([producer_id, product])
            self.logger.info("Finished  publish product %s by prod id %d", product, producer_id)
            return True

        self.logger.info("Finished  publish product %s by prod id %d", product, producer_id)
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.cart_id_lock:
            self.logger.info("Starting  new_cart")
            # creez un nou cart
            self.list_of_carts[len(self.list_of_carts)] = []
            self.logger.info("Finished  new_cart")

        return len(self.list_of_carts) - 1

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        with self.stock_products_lock:
            self.logger.info("Starting  add %s to cart with id %d", product, cart_id)
            # caut produsul in stock
            for prod in self.stock_products:
                if prod[1] == product:
                    # Daca am gasit produsul in stock il scot din stoc si il adaug in cos
                    self.stock_products.remove(prod)
                    self.list_of_carts[cart_id].append([prod[0], product])
                    self.logger.info("Finished  add %s to cart with id %d", product, cart_id)
                    return True
            self.logger.info("Finished  add %s to cart with id %d", product, cart_id)
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("Starting  remove %s from cart with id %d ", product, cart_id)
        for produs in self.list_of_carts[cart_id]:
            if product == produs[1]:
                #  Am gasit produsul in cos, il adaug inapoi in stock si il scot din cos
                self.stock_products.append(produs)
                self.list_of_carts[cart_id].remove(produs)
                break
        self.logger.info("Finished  remove %s from cart with id %d ", product, cart_id)


    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        cart_list = []
        with self.place_order_lock:
            self.logger.info("Starting place order for cart with id %d ", cart_id)
            for prod in self.list_of_carts[cart_id]:
                #  Fac lista cu produsele din cos, le scad din coada producatorilor si printez
                print(currentThread().name, "bought", prod[1])
                cart_list.append(prod[1])
                self.producers_queue_len[prod[0]] -= 1
            self.logger.info("Finished place order for cart with id %d ", cart_id)
        return cart_list

class TestMarketplace(unittest.TestCase):
    """  Unit Tests  """

    def setUp(self):
        """Initializations"""
        self.marketplace = Marketplace(2)
        self.stock_products = [Tea("Tei", 10, "Herbal"),
        Coffee(name='Cappuccino', price=2, acidity=4.02, roast_level='MEDIUM')]

    def test_register_producer(self):
        """ Register 2 producers """
        self.assertEqual(self.marketplace.register_producer(), 0, "register FAILED")
        self.assertEqual(self.marketplace.register_producer(), 1, "register FAILED")

    def test_publish(self):
        """ Publish 3 products with queue size = 2 """
        prod_id = self.marketplace.register_producer()
        self.assertTrue(self.marketplace.publish(prod_id, self.stock_products[1]), "publish FAIL")
        self.assertTrue(self.marketplace.publish(prod_id, self.stock_products[0]), "publish FAIL")
        self.assertFalse(self.marketplace.publish(prod_id, self.stock_products[0]), "publish FAIL")


    def test_new_cart(self):
        """ Register new cart """
        self.assertEqual(self.marketplace.new_cart(), 0, "new_cart FAILED")
        self.assertEqual(self.marketplace.new_cart(), 1, "new_cart FAILED")

    def test_add_to_cart(self):
        """
        Publish 2 products, register a cart, one producer and add only 2 products
        """
        prod_id = self.marketplace.register_producer()
        self.marketplace.publish(prod_id, self.stock_products[1])
        self.marketplace.publish(prod_id, self.stock_products[0])
        cart_id = self.marketplace.new_cart()
        first_add = self.marketplace.add_to_cart(cart_id, self.stock_products[1])
        self.assertTrue(first_add, "add_to_cart FAILED")
        second_add = self.marketplace.add_to_cart(cart_id, self.stock_products[0])
        self.assertTrue(second_add, "add_to_cart FAILED")
        third_add = self.marketplace.add_to_cart(cart_id, self.stock_products[0])
        self.assertFalse(third_add, "add_to_cart FAILED")

    def test_remove_from_cart(self):
        """
        Publish 2 products, add 2 products to cart, remove one and another one.
        """
        prod_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        self.marketplace.publish(prod_id, self.stock_products[1])
        self.marketplace.publish(prod_id, self.stock_products[0])
        self.marketplace.add_to_cart(cart_id, self.stock_products[0])
        self.marketplace.add_to_cart(cart_id, self.stock_products[1])
        self.marketplace.remove_from_cart(cart_id, self.stock_products[0])
        self.assertEqual(len(self.marketplace.list_of_carts[0]), 1, "remove_from_cart FAILED")
        self.marketplace.remove_from_cart(cart_id, self.stock_products[0])
        self.assertEqual(len(self.marketplace.list_of_carts[0]), 1, "remove_from_cart FAILED")

    def test_place_order(self):
        """
        Place an order with 2 producs.
        """
        prod_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        self.marketplace.publish(prod_id, self.stock_products[1])
        self.marketplace.publish(prod_id, self.stock_products[0])
        self.marketplace.add_to_cart(cart_id, self.stock_products[0])
        self.marketplace.add_to_cart(cart_id, self.stock_products[1])
        self.marketplace.remove_from_cart(cart_id, self.stock_products[0])
        self.marketplace.add_to_cart(cart_id, self.stock_products[0])
        products_ref = [self.stock_products[1], self.stock_products[0]]
        products_out = self.marketplace.place_order(cart_id)
        for prod in products_out:
            self.assertIn(prod, products_ref, "place_order FAILED")
