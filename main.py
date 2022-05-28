import serial
import time
import RPi.GPIO as GPIO


class GripperIAI:
    def __init__(self,port='/dev/ttyUSB0',baudrate=38400,timeout=3,relay_pin=18, target_location=(50,50,50), desired_location=(0,0,0)):
        
        # Set the port and baudrate for serial communication
        self.port = port
        self.baudrate = baudrate
        
        self.timeout = timeout
        
        self.ser = serial.Serial(self.port, self.baudrate, timeout= self.timeout)
        
        # Set up the GPIO for relay
        self.relay_pin = relay_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relay_pin,GPIO.OUT)
        
        # Turn on the servo
        self.activate()
        
        #Set Home
        self.set_home()
        
        # Set target and desired location
        self.target_location = target_location
        self.desired_location = desired_location
    
    def activate(self):
        
        # Command to turn on the servo
        self.ser.write('!00232071b0\r\n'.encode())
        read = self.ser.readline().decode()
        print('Activating Servo...')
        print(read+'\n')

        time.sleep(1)
    
    def set_home(self):
        
        # Function to command the robot to return to origin point

        self.ser.write('!0023307000000a0\r\n'.encode())
        read = self.ser.readline().decode()
        print(read+'\n')
        read = self.ser.readline().decode()
        print("Resetting Position")
        print(read+'\n')
        
        # Wait for the robot to finish
        time.sleep(5)



    def move(self,message_id='absolute',axis='xyz',acceleration=1.0,speed=50,x_target=0,y_target=0,z_target=0) :
        
        target_speed = speed
        moving = message_id
        
        if message_id == 'absolute' :
            message_id = '234'
        elif  message_id == 'relative' :
            message_id = '235'

        axis_pattern = 0b0
        if 'x' in axis :
            axis_pattern = axis_pattern + 0b1
        if 'y' in axis :
            axis_pattern = axis_pattern + 0b10    
        if 'z' in axis :
            axis_pattern = axis_pattern + 0b100    
        byte_format = 2
        byte_adding = byte_format - len(hex(axis_pattern).lstrip('0x'))
        adding_text = ''
        for i in range(0,byte_adding):
            adding_text = adding_text + '0'
        axis_pattern = adding_text + hex(axis_pattern).lstrip('0x')

        byte_format = 4
        byte_adding = byte_format - len(hex(int(acceleration*100)).lstrip('0x'))
        adding_text = ''
        for i in range(0,byte_adding):
            adding_text = adding_text + '0'
        acceleration = adding_text + hex(int(acceleration*100)).lstrip('0x')

        byte_format = 4
        byte_adding = byte_format - len(hex(int(speed)).lstrip('0x'))
        adding_text = ''
        for i in range(0,byte_adding):
            adding_text = adding_text + '0'
        speed = adding_text + hex(int(speed)).lstrip('0x')

        position = '';
        byte_format = 8
        if 'x' in axis :
            if x_target >=0 :
                byte_adding = byte_format - len(hex(int(x_target*1000)).lstrip('0x'))
                adding_text = ''
                for i in range(0,byte_adding):
                    adding_text = adding_text + '0'            
                position = position + adding_text + hex(int(x_target*1000)).lstrip('0x')
            else :
                x_target = -x_target
                position = position + hex(int(16**byte_format - x_target*1000)).lstrip('0x')
        if 'y' in axis :
            if y_target >=0 :
                byte_adding = byte_format - len(hex(int(y_target*1000)).lstrip('0x'))
                adding_text = ''
                for i in range(0,byte_adding):
                    adding_text = adding_text + '0'            
                position = position + adding_text + hex(int(y_target*1000)).lstrip('0x')
            else :
                y_target = -y_target
                position = position + hex(int(16**byte_format - y_target*1000)).lstrip('0x')
        if 'z' in axis :
            if z_target >=0 :
                byte_adding = byte_format - len(hex(int(z_target*1000)).lstrip('0x'))
                adding_text = ''
                for i in range(0,byte_adding):
                    adding_text = adding_text + '0'            
                position = position + adding_text + hex(int(z_target*1000)).lstrip('0x')
            else :
                z_target = -z_target
                position = position + hex(int(16**byte_format - z_target*1000)).lstrip('0x')

        string_command = '!00'+ message_id + axis_pattern + acceleration + acceleration + speed + position

        checksum = 0
        for i in range(0,len(string_command)) :
            checksum = checksum + ord(string_command[i])
        checksum = hex(int(checksum)).lstrip('0x')
        checksum = checksum[len(checksum)-2:len(checksum)]

        string_command = string_command + checksum

        self.ser.write((string_command +'\r\n').encode())
        print('Moving {}ly to x: {}, y: {}, z: {} with speed: {}'.format(moving, x_target, y_target, z_target, target_speed))
        read = self.ser.readline().decode()
        if (read[0]=='#'):
            print("Success")
        else:
            print("Error")
            print(read+'\n')
        time.sleep(3)
        
    def close_gripper(self):
        
        GPIO.output(self.relay_pin,1)
        time.sleep(2)
        
    def open_gripper(self):
        
        GPIO.output(self.relay_pin,0)
        time.sleep(2)
        
    def move_and_grip(self):
        
        #Gripper open
        self.open_gripper()
        
        # Move to target location
        self.move(x_target=self.target_location[0])
        self.move(x_target=self.target_location[0],y_target=self.target_location[1])
        self.move(x_target=self.target_location[0],y_target=self.target_location[1],z_target=self.target_location[2])
        
        #Gripper close
        self.close_gripper()
        
        
        # Move to desired Location
        self.move(x_target=self.target_location[0],y_target=self.target_location[1])
        self.move(x_target=self.target_location[0],y_target=self.desired_location[1])
        self.move(x_target=self.desired_location[0],y_target=self.desired_location[1])
        self.move(x_target=self.desired_location[0],y_target=self.desired_location[1],z_target=self.desired_location[2])
        
        # Open Gripper
        self.open_gripper()
        
    def __call__(self):
        
        while True:
            
            ans = str(input('Object Placed?: '))
            if(ans.lower()=='y' or ans.lower()=='yes'):
                self.move_and_grip()
            elif(ans.lower()=='quit' or ans.lower()=='exit'):
                break
            else:
                continue
                
        
    
gripper = GripperIAI(target_location=(60,100,75),desired_location=(0,0,75))
gripper()

#gripper.move('absolute','xyz',acceleration=1.0,speed=50,x_target=200,y_target=200,z_target=100)


    
