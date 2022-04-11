"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.marketplace = marketplace
        self.carts = carts
        self.retry_wait_time = retry_wait_time
        self.my_items = []

    def run(self):
        for cart_operations in self.carts:
            cart_id = self.marketplace.new_cart()
            # pentru fiecare runda de cumparaturi.
            for operatie in cart_operations:
                if operatie["type"] == "add":
                    i = 0
                    # incerc sa adug in cos toata cantitatea.
                    while i < operatie["quantity"]:
                        can_add = self.marketplace.add_to_cart(
                            cart_id=cart_id,
                            product=operatie["product"])
                        if not can_add:
                            time.sleep(self.retry_wait_time)
                        else:
                            i += 1
                elif operatie["type"] == "remove":
                    i = 0
                    # scot din cos toata cantitatea.
                    while i < operatie["quantity"]:
                        self.marketplace.remove_from_cart(
                            cart_id=cart_id,
                            product=operatie["product"])
                        i += 1
            # plasez comanda
            self.marketplace.place_order(cart_id)
