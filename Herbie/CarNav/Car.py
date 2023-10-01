from Herbie.Network.Client import Client
from Herbie.CarNav.Base import BaseController

from typing import List, Tuple, Union, Iterable
import time

class Car:
    
    def __init__(
            self, controller: BaseController, client: Union[Client, None] = None,
            ) -> None:
        
        self.controller_ = controller
        self.client_ = client
        if self.client_:
            self.client_.connect()

    async def drive(self):
        try:
            for status in self.controller_.drive():
                self.send_server_data_()
        except Exception as e:
            self.shutdown()
            raise e

    def send_server_data_(self):
        if self.client_:
            self.client_.send(self.controller_.get_log_data())
    
    def shutdown(self) -> None:
        self.controller_.shutdown()
        if self.client_:
            self.client_.shutdown()