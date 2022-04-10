"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
import logging
from logging.handlers import RotatingFileHandler
from threading import Lock, currentThread


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    logger = logging.getLogger('marketplace.log')
    handler = RotatingFileHandler("marketplace.log", maxBytes=20000, backupCount=10)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    handler.setFormatter(formatter)
    logging.Formatter.converter = time.gmtime
    logger.addHandler(handler)

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        # key = producer_id, value = nr products in queue
        self.producers_size = {}
        # list of lists [id_producer, product]
        self.products = []

        # key - id_cart, val - list of tuples [id_producer, product]
        self.list_of_carts = {}
        self.nr_carts = 0

        self.queue_size_per_producer = queue_size_per_producer
        # Producers locks
        self.producers_id = Lock()
        # Consumers locks
        self.cart_id = Lock()
        self.place_order_lock = Lock()
        self.products_lock = Lock()




    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.producers_id:
            self.logger.info("Starting  register_producer")
            self.producers_size[len(self.producers_size)] = 0
            self.logger.info("Finished  register_producer")
        return len(self.producers_size) - 1

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
        if self.producers_size[producer_id] < self.queue_size_per_producer:
            self.producers_size[producer_id] += 1
            self.products.append([producer_id, product])

            self.logger.info("Finished  publish product %s by prod id %d", product, producer_id)
            return True

        self.logger.info("Finished  publish product %s by prod id %d", product, producer_id)
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.cart_id:
            self.logger.info("Starting  new_cart")
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
        # Daca produsul e disponibil il adauga in cart si returneaza True,
        # altfel returneaza False

        with self.products_lock:
            self.logger.info("Starting  add_to_cart")
            for prod in self.products:
                if prod[1] == product:
                    self.products.remove(prod)
                    self.list_of_carts[cart_id].append([prod[0], product])
                    self.logger.info("Finished  add_to_cart")
                    return True
            self.logger.info("Finished  add_to_cart")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("Starting  remove_from_cart")
        for produs in self.list_of_carts[cart_id]:
            if product == produs[1]:
                self.products.append(produs)
                self.list_of_carts[cart_id].remove(produs)
                break
        self.logger.info("Finished remove_from_cart")


    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        cart_list = []
        with self.place_order_lock:
            self.logger.info("Starting place_order")
            for prod in self.list_of_carts[cart_id]:
                print(currentThread().name, "bought", prod[1])
                cart_list.append(prod[1])
                self.producers_size[prod[0]] -= 1
            self.logger.info("Finished place_order")
        return cart_list
