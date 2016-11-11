#List of required functions

#To do
	#Get GPS working with pi
	#Use GPS time to set Pi time before logging time in log file	

import math, smbus, time

bus = smbus.SMBus(1)
ard_bus = smbus.SMBus(1)
mag_address = 0x1D
accel_address = 0x1D
gyro_address = 0x6B
ard_addr = 0x08

#Mag
reg_5 = 0x24	#Temperature, resolution, frequency
reg_6 = 0x25	#Range
reg_7 = 0x26	#Mode
OUT_X_L_M = 0x08
OUT_Y_L_M = 0x0A
OUT_Z_L_M = 0x0C
OUT_X_H_M = 0x09
OUT_Y_H_M = 0x0B
OUT_Z_H_M = 0x0D

#Accel
reg_1 = 0x20
reg_2 = 0x21
OUT_X_L_A = 0x28
OUT_Y_L_A = 0x2A
OUT_Z_L_A = 0x2C
OUT_X_H_A = 0x29
OUT_Y_H_A = 0x2B
OUT_Z_H_A = 0x2D

#Gyro
reg_1_G = 0x20
reg_2_G = 0x21
reg_4_G = 0x23
OUT_X_L_G = 0x28
OUT_X_H_G = 0x29
OUT_Y_L_G = 0x2A
OUT_Y_H_G = 0x2B
OUT_Z_L_G = 0x2C
OUT_Z_H_G = 0x2D

x_cal = 0
y_cal = 0
z_cal = 0
x_gyro_cal = 0
y_gyro_cal = 0
z_gyro_cal = 0
x_mag_cal = 0
y_mag_cal = 0
z_mag_cal = 0
pre = [0.0] * 10
cur = [0.0] * 10
run_main = True
data_array = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]	#lon, lat, alt, head, pitch, roll, yaw, time

def main_loop_for_control():
	global run_main
	while(run_main):
		read_accel()
		read_gyro()
		read_mag()
		read_time()
		# UPDATE AHRS DATA
		if (cur[0] - pre[0] >= 1.0):
			log_data()

def return_data():
	return data_array

def update_run_state(update):
	global run_main
	if update == False:
		run_main = False
'''
def AHRS_Update():
'''
def setup_IMU_sensor():
	global cur
	global x_cal
	global y_cal
	global z_cal
	global x_gyro_cal
	global y_gyro_cal
	global z_gyro_cal
	global x_mag_cal
	global y_mag_cal
	global z_mag_cal
	#Mag
	bus.write_byte_data(mag_address, reg_5, 0b11110000)	#Temp enabled, high res, 50Hz 
	bus.write_byte_data(mag_address, reg_6, 0b00100000)	#+/- 4 gauss
	bus.write_byte_data(mag_address, reg_7, 0b00000000)	#Normal mode, continuous-conversion mode
	#Accel
	bus.write_byte_data(accel_address, reg_1, 0b01100111)	#Enable all axis, continuos, 100Hz
	bus.write_byte_data(accel_address, reg_2, 0b00001000)	#+/- 4G
	#Gyro
	bus.write_byte_data(gyro_address, reg_1_G, 0b00001111)	#Enable all axis
	bus.write_byte_data(gyro_address, reg_2_G, 0b00110000)	#Continuos
	bus.write_byte_data(gyro_address, reg_4_G, 0b00000000)	#245dps
	time.sleep(1)

	#Set calibration data
	for i in range(100):	#Calibrate accel and gyro using the average of 100 data points
		temp_value_x = bus.read_byte_data(accel_address, OUT_X_L_A) | bus.read_byte_data(accel_address, OUT_X_H_A) << 8
		temp_value_y = bus.read_byte_data(accel_address, OUT_Y_L_A) | bus.read_byte_data(accel_address, OUT_Y_H_A) << 8
		temp_value_z = bus.read_byte_data(accel_address, OUT_Z_L_A) | bus.read_byte_data(accel_address, OUT_Z_H_A) << 8
		temp_gyro_x = bus.read_byte_data(gyro_address, OUT_X_L_G) | bus.read_byte_data(gyro_address, OUT_X_H_G) << 8
		temp_gyro_y = bus.read_byte_data(gyro_address, OUT_Y_L_G) | bus.read_byte_data(gyro_address, OUT_Y_H_G) << 8
		temp_gyro_z = bus.read_byte_data(gyro_address, OUT_Z_L_G) | bus.read_byte_data(gyro_address, OUT_Z_H_G) << 8
		if (temp_value_x & (1 << (16 - 1))) != 0:
			value_x = float(temp_value_x - (1 << 16))
		else:
			value_x = float(temp_value_x)
		if (temp_value_y & (1 << (16 - 1))) != 0:
			value_y = float(temp_value_y - (1 << 16))
		else:
			value_y = float(temp_value_y)
		if (temp_value_z & (1 << (16 - 1))) != 0:
			value_z = float(temp_value_z - (1 << 16))
		else:
			value_z = float(temp_value_z)
		if (temp_gyro_x & (1 << (16 - 1))) != 0:
			gyro_x = float(temp_gyro_x - (1 << 16))
		else:
			gyro_x = float(temp_gyro_x)
		if (temp_gyro_y & (1 << (16 - 1))) != 0:
			gyro_y = float(temp_gyro_y - (1 << 16))
		else:
			gyro_y = float(temp_gyro_y)
		if (temp_gyro_z & (1 << (16 - 1))) != 0:
			gyro_z = float(temp_gyro_z - (1 << 16))
		else:
			gyro_z = float(temp_gyro_z)
		x_cal = x_cal + (value_x * 8.0/65536.0)
		y_cal = y_cal + (float(value_y) * 8.0/65536.0)
		z_cal = z_cal + (float(value_z) * 8.0/65536.0)
		x_gyro_cal = x_gyro_cal + (float(gyro_x) * 490.0 / 65536.0)
		y_gyro_cal = y_gyro_cal + (float(gyro_y) * 490.0 / 65536.0)
		z_gyro_cal = z_gyro_cal + (float(gyro_z) * 490.0 / 65536.0)
	x_cal = x_cal / 100
	y_cal = y_cal / 100
	z_cal = z_cal / 100
	x_gyro_cal = x_gyro_cal / 100
	y_gyro_cal = y_gyro_cal / 100
	z_gyro_cal = z_gyro_cal / 100
	print('Accel Average value = %0.2f, %0.2f, %0.2f' %(x_cal, y_cal, z_cal))
	print('Gyro Average value = %0.2f, %0.2f, %0.2f' %(x_gyro_cal, y_gyro_cal, z_gyro_cal))
	x_cal = 0 - x_cal
	y_cal = 0 - y_cal
	z_cal = 1 - z_cal
	x_gyro_cal = 0 - x_gyro_cal
	y_gyro_cal = 0 - y_gyro_cal
	z_gyro_cal = 0 - z_gyro_cal
	print('Accel CAL = %0.2f, %0.2f, %0.2f' %(x_cal, y_cal, z_cal))
	print('Gyro CAL = %0.2f, %0.2f, %0.2f' %(x_gyro_cal, y_gyro_cal, z_gyro_cal))
	try:	#Create data log file
		current_time = time.strftime("%Y%m%d_%H:%M:%S")
		log_file = open('Data_Log__' + current_time + '.dat','w')
		cur[0] = time.time()
		log_file.write('Cal: %0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,no_mag_cal,no_mag_cal,no_mag_cal,%0.4f' %(x_cal, y_cal, z_cal, x_gyro_cal, y_gyro_cal, z_gyro_cal, cur[0]))
	except:
		print('Failed to create log file')

def write_to_arduino(int_to_send):
	print('Integer to send value: %d' %int_to_send)
	n1 = int(int_to_send / 1000)
	n2 = int(int_to_send - n1 * 1000)
	ard_bus.write_i2c_block_data(ard_addr, n1, [n2])

def read_mag():
	mag_out_x = bus.read_byte_data(mag_address, OUT_X_L_M) | bus.read_byte_data(mag_address, OUT_X_H_M) << 8
	mag_out_y = bus.read_byte_data(mag_address, OUT_Y_L_M) | bus.read_byte_data(mag_address, OUT_Y_H_M) << 8
	mag_out_z = bus.read_byte_data(mag_address, OUT_Z_L_M) | bus.read_byte_data(mag_address, OUT_Z_H_M) << 8
	if (mag_out_x & (1 << (16 - 1))) != 0:
		mag_fix_x = float(mag_out_x - (1 << 16))
	else:
		mag_fix_x = float(mag_out_x)
		
	if (mag_out_y & (1 << ( 16 - 1))) != 0:
		mag_fix_y = float(mag_out_y - (1 << 16))
	else:
		mag_fix_y = float(mag_out_y)
		
	if (mag_out_z & (1 << ( 16 - 1))) != 0:
		mag_fix_z = float(mag_out_z - (1 << 16))
	else:
		mag_fix_z = float(mag_out_z)
	mag_fix_x = mag_fix_x * 8.0/65536.0
	mag_fix_y = mag_fix_y * 8.0/65536.0
	mag_fix_z = mag_fix_z * 8.0/65536.0
	pre = cur
	cur[7] = mag_fix_x
	cur[8] = mag_fix_y
	cur[9] = mag_fix_z

def read_accel():
	global pre
	global cur
	accel_out_x = bus.read_byte_data(accel_address, OUT_X_L_A) | bus.read_byte_data(accel_address, OUT_X_H_A) << 8
	accel_out_y = bus.read_byte_data(accel_address, OUT_Y_L_A) | bus.read_byte_data(accel_address, OUT_Y_H_A) << 8
	accel_out_z = bus.read_byte_data(accel_address, OUT_Z_L_A) | bus.read_byte_data(accel_address, OUT_Z_H_A) << 8
	if (accel_out_x & (1 << (16 - 1))) != 0:
		accel_fix_x = float(accel_out_x - (1 << 16))
	else:
		accel_fix_x = float(accel_out_x)
	if (accel_out_y & (1 << ( 16 - 1))) != 0:
		accel_fix_y = float(accel_out_y - (1 << 16))
	else:
		accel_fix_y = float(accel_out_y)
	if (accel_out_z & (1 << ( 16 - 1))) != 0:
		accel_fix_z = float(accel_out_z - (1 << 16))
	else:
		accel_fix_z = float(accel_out_z)
	accel_fix_x = accel_fix_x * 8.0/65536.0 + x_cal
	accel_fix_y = accel_fix_y * 8.0/65536.0 + y_cal
	accel_fix_z = accel_fix_z * 8.0/65536.0 + z_cal
	pre = cur
	cur[1] = accel_fix_x
	cur[2] = accel_fix_y
	cur[3] = accel_fix_z
	
def read_gyro():
	gyro_out_x = bus.read_byte_data(gyro_address, OUT_X_L_G) | bus.read_byte_data(gyro_address, OUT_X_H_G) << 8
	gyro_out_y = bus.read_byte_data(gyro_address, OUT_Y_L_G) | bus.read_byte_data(gyro_address, OUT_Y_H_G) << 8
	gyro_out_z = bus.read_byte_data(gyro_address, OUT_Z_L_G) | bus.read_byte_data(gyro_address, OUT_Z_H_G) << 8
	if (gyro_out_x & (1 << (16 - 1))) != 0:
		gyro_fix_x = float(gyro_out_x - (1 << 16))
	else:
		gyro_fix_x = float(gyro_out_x)
	if (gyro_out_y & (1 << (16 - 1))) != 0:
		gyro_fix_y = float(gyro_out_y - (1 << 16))
	else:
		gyro_fix_y = float(gyro_out_y)
	if (gyro_out_z & (1 << (16 - 1))) != 0:
		gyro_fix_z = float(gyro_out_z - (1 << 16))
	else:
		gyro_fix_z = float(gyro_out_z)
	gyro_fix_x = gyro_fix_x * 490.0 / 65536.0 + x_gyro_cal
	gyro_fix_y = gyro_fix_y * 490.0 / 65536.0 + y_gyro_cal
	gyro_fix_z = gyro_fix_z * 490.0 / 65536.0 + z_gyro_cal
	pre = cur
	cur[4] = gyro_fix_x
	cur[5] = gyro_fix_y
	cur[6] = gyro_fix_z
	
def read_time():
	pre = cur
	cur[0] = time.time()
	
def distance(x1, x2, y1, y2, z1, z2):
	return math.sqrt(pow(x2-x1,2) + pow(y2-y1,2) + pow(z2-z1,2))
	
def telemetry(x1,x2,y1,y2,z1,z2):	#Computes the yaw and pitch angles between the base station and craft
	temp_array = convert(x1,x2,y1,y2,z1,z2)	#Calls convert function to change lat/lon to meters
	rad_yaw = math.atan((temp_array[3]-temp_array[2])/(temp_array[1]-temp_array[0]))
	rad_pitch = math.asin((z2-z1)/distance(temp_array[0],temp_array[1],temp_array[2],temp_array[3],z1,z2))
	return [math.degrees(rad_yaw),math.degrees(rad_pitch)]	#Returns the two degrees for the antenna to point
	
def convert(x1,x2,y1,y2,z1,z2):	#Converts lat/lon to meters
	print([0,abs((x2-x1)*111320),0,abs((y2-x1)*111320),z1,z2])
	return [0,(x2-x1)*111320,0,(y2-x1)*111320,z1,z2]

def log_data():
	log_file.write('%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f,%0.4f' %(cur[0], cur[1], cur[2], cur[3], cur[4], cur[5], cur[6], cur[7], cur[8], cur[9]))

def end_of_control():
	log_file.close()