import sys
import pygame
import socket
import math

# Change these to change which inputs control what.
# Note: Servos cannot use triggers
CONTROLLER = {"front": "rx",  # servos
              "rear_x": "lx",
              "rear_z": "ly",
              "front_l": "lt",  # motors
              "front_r": "rt",
              "rear": "ry"}

# Indexes for the axes as defined on the controller.
AXES = {"lx": 0,
        "ly": 1,
        "lt": 5,
        "rx": 2,
        "ry": 3,
        "rt": 4}

# Width and height of interface
WIDTH = 700
HEIGHT = 800

# Colors to be used on the interface
BLACK = (0, 0, 0)  # background
WHITE = (255, 255, 255)  # skeleton
RED = (255, 0, 0)  # servos
BLUE = (0, 135, 255)  # motors

# Set the target to the Pico
if len(sys.argv) == 4:
    (TARGET_IP, SERVO_PORT, MOTOR_PORT) = sys.argv[1:]
    print(f"Target IP: {TARGET_IP} Servo Port: {SERVO_PORT} Motor Port: {MOTOR_PORT}")
else:
    (TARGET_IP, SERVO_PORT, MOTOR_PORT) = ('127.0.0.1', 8000, 8001)
    print("No target IP or port specified. Using localhost and ports 8000 and 8001.")


# Account for quirks in the controller inputs
def _normalized_joystick(value, axis):
    match axis[1]:
        case 'y':
            return -value  # Up and down are flipped in the y direction
        case 't':
            return (value + 1) / 2  # By default, -1 is resting and 1 is fully engaged
        case _:
            return value


# Draw the rear motor at an angle from the back of the axle.
# For some reason pygame won't do this properly by default.
# This also accounts for the conversion between the servo angle and the actual position of the motor.
def _draw_rear_motor_at_angle(screen, pivot, motor_width, motor_height, angle):
    angle = (90 - angle) * math.pi / 90

    a = (pivot[0] - (motor_width / 2) * math.cos(angle), pivot[1] + (motor_width / 2) * math.sin(angle))
    b = (pivot[0] + (motor_width / 2) * math.cos(angle), pivot[1] - (motor_width / 2) * math.sin(angle))
    c = (a[0] + motor_height * math.sin(angle), a[1] + motor_height * math.cos(angle))
    d = (c[0] + motor_width * math.cos(angle), c[1] - motor_width * math.sin(angle))

    pygame.draw.polygon(screen, WHITE, (a, b, d, c))


class Controller:
    def __init__(self, joystick_id=0):
        self.js = pygame.joystick.Joystick(joystick_id)

    def get(self, device):
        return self.js.get_axis(AXES[CONTROLLER[device]])


class Servos:
    def __init__(self):
        self.front = 90  # Starts at 90 degrees to face parallel to the ground. Ranges from 0 to 180
        self.rear_x = 90  # Starts at 90 degrees to face directly backward, Ranges from 0 to 180
        self.rear_z = 90  # Starts at 90 degrees to be parallel to the ground. Ranges from 0 to 180

        # Create socket to communicate with the blimp
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self):
        self.sock.sendto(f"{self.front},{self.rear_x},{self.rear_z}".encode(), (TARGET_IP, SERVO_PORT))

    def set(self, servo, value):
        value = 90 * (_normalized_joystick(value, CONTROLLER[servo]) + 1)
        if servo == "front":
            self.front = value
        elif servo == "rear_x":
            self.rear_x = value
        elif servo == "rear_z":
            self.rear_z = value


class Motors:
    def __init__(self):
        self.front_l = 0  # All motors have zero speed by default
        self.front_r = 0
        self.rear = 0

        # Create socket to communicate with the blimp
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self):
        self.sock.sendto(f"{self.front_l},{self.front_r},{self.rear}".encode(), (TARGET_IP, MOTOR_PORT))

    def set(self, motor, value):
        value = _normalized_joystick(value, CONTROLLER[motor])

        # Account for the case where a trigger is not used
        if CONTROLLER[motor][1] != "t" and value < 0:
            value = 0

        if motor == "front_l":
            self.front_l = value
        elif motor == "front_r":
            self.front_r = value
        elif motor == "rear":
            self.rear = value


def main():
    pygame.init()

    # initialize servos and motors
    servos = Servos()
    motors = Motors()

    # Get controller
    controller = Controller()

    # create window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BLIMP")
    pygame.display.set_icon(pygame.image.load('icon.jpg'))

    # set clock
    clock = pygame.time.Clock()

    # main loop
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    done = True

        # clear screen
        screen.fill(BLACK)

        # Create graphics
        offset = 100

        # General motor dimensions
        motor_width = 50
        motor_height = 75

        # Center axis
        pygame.draw.line(screen, WHITE, ((WIDTH - offset)//2, HEIGHT//4), ((WIDTH - offset)//2, 3*HEIGHT//4), 3)

        # Rear motor
        _draw_rear_motor_at_angle(screen, ((WIDTH - offset)//2, 3*HEIGHT//4), motor_width, motor_height, servos.rear_x)

        # front motor assembly
        pygame.draw.line(screen, WHITE, ((WIDTH - offset)//4, HEIGHT//4), (3*(WIDTH - offset)//4, HEIGHT//4), 3)

        # set font
        font = pygame.font.Font(None, 20)

        # Add text
        motor_padding = 30

        front_l_text = font.render(f"{motors.front_l:.2f}", True, BLUE)
        front_l_rect = front_l_text.get_rect()
        front_l_rect.center = ((WIDTH - offset - motor_padding - 2*front_l_text.get_width())//4, HEIGHT//4)
        screen.blit(front_l_text, front_l_rect)

        front_r_text = font.render(f"{motors.front_r:.2f}", True, BLUE)
        front_r_rect = front_r_text.get_rect()
        front_r_rect.center = (3*(WIDTH - offset + motor_padding)//4, HEIGHT//4)
        screen.blit(front_r_text, front_r_rect)

        rear_text = font.render(f"{motors.rear:.2f}", True, BLUE)
        rear_rect = rear_text.get_rect()
        rear_rect.center = ((WIDTH - offset)//2, 3*HEIGHT//4 + rear_rect.height // 2)
        screen.blit(rear_text, rear_rect)

        # Update values from controller
        for servo in ["front", "rear_x", "rear_z"]:
            servos.set(servo, controller.get(servo))
        for motor in ["front_l", "front_r", "rear"]:
            motors.set(motor, controller.get(motor))

        # Send values to the blimp
        servos.send()
        motors.send()

        # Update screen and set frame rate
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
