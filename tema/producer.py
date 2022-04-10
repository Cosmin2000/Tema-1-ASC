"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread

class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time

    def run(self):
        prod_id = self.marketplace.register_producer()
        while True:
            for product in self.products:
                i = 0
                # public fiecare produs(in cantitatea dorita)
                quantity = product[1]
                prod = product[0]
                reproduce_time = product[2]
                while i < int(quantity):
                    not_full_queue = self.marketplace.publish(producer_id=prod_id,
                                                              product=prod)
                    if not_full_queue:
                        time.sleep(reproduce_time)
                        i += 1
                    else:
                        time.sleep(self.republish_wait_time)
