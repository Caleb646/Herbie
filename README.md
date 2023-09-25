# Herbie the Self-Driving RC Car

This Python library is designed to help you build and control a self-driving RC car using a Raspberry Pi. 
Whether you're a beginner or an experienced, this library provides a modular framework that allows you 
to mix and match various components, such as sensors, cameras, controller types, and drive trains, to create your own customized self-driving RC car.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Features
- Modular architecture: Easily swap out or add new components to your RC car setup.
- Self-driving capability: Implement autonomous driving algorithms using the library's sensor and camera modules.
- Manual control: Use a controller to take the wheel when you want to drive the car manually.
- Extensible: Create custom components or algorithms to expand the functionality of your RC car.
- User-friendly: Designed with simplicity in mind to make it accessible to hobbyists and learners.

## Installation
1. Clone this repository to your Raspberry Pi:
   ```bash
   git clone https://github.com/Caleb646/Herbie.git
   cd Herbie
   ```
2. Basic Install:
   ```bash
   pip install .
   ```
3. Install with PiCamera:
   ```bash
   pip install[PiCamera] .
   ```
4. Install with TFLite:
   ```bash
   pip install[TFLite] .
   ```
5. Install with Both:
   ```bash
   pip install[PiCamera,TFLite] .
   ```
6. Additional Dependendies
- [Picar-4wd](https://github.com/sunfounder/picar-4wd.git) is needed if any of non-base Hardware classes are used such as DriveTrain or UltraSonic.

## Usage

### Getting Started

1. Import the library into your Python project:
   ```python
   from Herbie.CarNav.Api import Car, AutonomousController, TFDetector
   from Herbie.Hardware.Api import DriveTrain, UltraSonic, Camera
   from Herbie.Network.Api import Client
   ```

2. Initialize the car and chosen controller:
   ```python
   car = Car(
       AutonomousController(
            map_size = 11, # how big the grid the car exists in will be.
            cell_size = 25, # how big each cell in the grid is in centimeters.
            target = Position(9, 9), # the x, y position in the car's map that it needs to drive to.
            drive_train = DriveTrain(), # the drivetrain controls how the car rotates and moves forwards and backwards.
            obstacle_sensor = UltraSonic(), # the ultrasonic is how the car detects obstacles it needs to avoid.
            detector = TFDetector(Camera(), model_path="path to detection model")) # the class responsible for detecting various objects using the car's camera.
       ),
       # Client is an optional argument. It is a standard socket client that connects to a server and sends
       # data about the car's position, current obstacles, and the current path the car has chosen to take.
       Client() 
   )
    ```
3. Tell the car to drive and shutdown gracefully if an error is encountered:
      ```python
        try:
            car.drive()
        except Exception as e:
            car.shutdown()
            raise e
      ```

### Creating Custom Components
Herbie is made up of four modules CarNav, CMath, Hardware, and Network. In each module there is a Base.py file. Each Base.py is only dependent on the CPython3 standard library. 
So they can be imported and used to create a user specified class that can be used with the higher level classes. For example: 

1. Creating a custom sensor class.
    ```python
    from Herbie.Hardware.Base import BaseSensor
    
    class MySensor(BaseSensor):
        # Below are the only methods required for the Sensor to be able to interact with the higher level
        # classes such as AutonomousController.
        def get_distance(self) -> float:
            """Implementation"""
        def move_sensor_to(self, angle: float) -> bool:
            """Implementation"""

    # Now all that is needed to use this class is to pass it to the Controller class when setting up the car.
    car = Car(
    ...
    AutonomousController(
            ....
            MySensor()
        )
    )
    # This will create a car that uses your sensor for obstacle detection.
    ```

## Examples
Check out the `Examples/` directory for sample code using this library. These examples can help you understand how to build and program your RC car.

## License
This project is licensed under the MIT License.

---

Happy driving with your Raspberry Pi Self-Driving RC Car!
