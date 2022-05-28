import serial
import time

set_port = 'COM7' # Please check the port at Device Manager
set_baudrate = 38400
set_timeout = 3

ser = serial.Serial(set_port,set_baudrate,timeout=set_timeout)
ser.write('!00232071b0\r\n'.encode())
read = ser.readline().decode()
print(read+'\n')

time.sleep(1)

ser.write('!0023307000000a0\r\n'.encode())
read = ser.readline().decode()
print(read+'\n')

time.sleep(5)



def IAI_Robot_Move(ser,message_id,axis,acceleration,speed,x_target,y_target,z_target) :
    
# IAI_Robot_Move(ser,'relative','xz',0.3,100,50,50,0)

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

    ser.write((string_command +'\r\n').encode())
    read = ser.readline().decode()
    print(read+'\n')
    
# IAI_Robot_Move(ser,'relative','xyz',acceleration=0.3,speed=100,x_target=50,y_target=0,z_target=0)
# time.sleep(5)