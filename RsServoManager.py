#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
# ver1.21117
# (C) 2012 Matsuda Hiroaki

"""
 \file RsServoManager.py
 \brief It is the component that controls the servo RSX0X
 \date $Date$


"""
import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# Import RS module
import pyrs
import ConfigParser as Conf

# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
rsservomanager_spec = ["implementation_id", "RsServoManager", 
		 "type_name",         "RsServoManager", 
		 "description",       "It is the component that controls the servo RSX0X", 
		 "version",           "1.0.0", 
		 "vendor",            "Matsuda Hiroaki", 
		 "category",          "Servo", 
		 "activity_type",     "STATIC", 
		 "max_instance",      "1", 
		 "language",          "Python", 
		 "lang_type",         "SCRIPT",
		 ""]
# </rtc-template>

class RsServoManager(OpenRTM_aist.DataFlowComponentBase):
	
	"""
	\class RsServoManager
	\brief It is the component that controls the servo RSX0X
	
	"""
	def __init__(self, manager):
		"""
		\brief constructor
		\param manager Maneger Object
		"""
		OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

		self._d_motion = RTC.TimedLongSeq(RTC.Time(0,0),[])
		"""
		"""
		self._motionIn = OpenRTM_aist.InPort("motion", self._d_motion)
		self._d_on_off = RTC.TimedLongSeq(RTC.Time(0,0),[])
		"""
		"""
		self._on_offIn = OpenRTM_aist.InPort("on_off", self._d_on_off)
		self._d_sensor = RTC.TimedLongSeq(RTC.Time(0,0),[])
		"""
		"""
		self._sensorOut = OpenRTM_aist.OutPort("sensor", self._d_sensor)

		# initialize of configuration-data.
		# <rtc-template block="init_conf_param">
		
		# </rtc-template>


		 
	def onInitialize(self):

		# Bind variables and configuration variable
		
		# Set InPort buffers
		self.addInPort("motion",self._motionIn)
		self.addInPort("on_off",self._on_offIn)
		
		# Set OutPort buffers
		self.addOutPort("sensor",self._sensorOut)
		
		# Set service provider to Ports
		
		# Set service consumers to Ports
		
		# Set CORBA Service Ports
		
		print('State:OnInitialize')
		
		# Read ini file
		self.conf = Conf.SafeConfigParser()
                self.conf.read('ini/rsservomanager.ini')
		
                self.port = self.conf.get('PORT', 'port')
                self.baudrate = int(self.conf.get('PORT', 'baudrate'))
                
		self.write_sens = self.conf.get('SERVO', 'write_sens') 
		self.servo_num = int(self.conf.get('SERVO', 'servo_num'))
                self.id = []
		for i in range(self.servo_num):
                        self.id.append(int(self.conf.get('SERVO', 'id_' + str(i + 1))))
                        
		self.pos_min = int(self.conf.get('POSITION', 'min'))
		self.pos_max = int(self.conf.get('POSITION', 'max'))
		self.offset = int(self.conf.get('POSITION', 'offset'))

		# Open serial port
                self.rs = pyrs.Rs()
		self.rs.open_port(self.port, self.baudrate)

		# Set multi servo value
		self.servo_on = []
		self.servo_pos = []
			
		return RTC.RTC_OK
	
	def onFinalize(self, ec_id):
		
		#Close port
		self.rs.close_port()
		print('Close Port %s' %self.port)
	
		return RTC.RTC_OK
	
	def onActivated(self, ec_id):
		
		print('State:OnActivated')
		
		return RTC.RTC_OK
	
	def onDeactivated(self, ec_id):
		
		print('State:OnDeactivated')
		
		#Close port
		self.rs.close_port()
		print('Close Port %s' %self.port)
	
		return RTC.RTC_OK
	
	def onExecute(self, ec_id):
		
		# Check Inport
		if self._motionIn.isNew():
			# _d_motion.data:[Flag, ID, Position, Time]
                        self._d_motion = self._motionIn.read()
                        #print 'Received:',self._d_motion

                        flag = self._d_motion.data[0]
			id = self._d_motion.data[1]
			pos = self._d_motion.data[2] + self.offset
			
			if pos < self.pos_min:
                                pos = self.pos_min
                        elif pos > self.pos_max:
                                pos = self.pos_max
                                
			time = self._d_motion.data[3]

                        if flag == 0:
                                self.rs.target_position(id, pos, time)
                                print('ID: %d Position: %d Time: %d' %(id, pos, time))

                        elif flag == 1:
                                self.servo_pos.append([id, pos, time])
                                if len(self.servo_pos) == self.servo_num:
                                        self.rs.multi_target_position(self.servo_pos)
                                        self.servo_pos = []
			
		if self._on_offIn.isNew():
			# _on_off.data:[Flag, ID, Servo ON/OFF]
                        self._d_on_off = self._on_offIn.read()
                        #print Received:',self._d_on_off

			flag = self._d_on_off.data[0]
			id = self._d_on_off.data[1]
			state = self._d_on_off.data[2]
			
			if flag == 0:
				self.rs.torque_on(id, state)
				print('Servo %d mode %d' %(id, state))

			elif flag == 1:
                                self.servo_on.append([id, state])
                                if len(self.servo_on) == self.servo_num:
                                        self.rs.multi_torque_on(self.servo_on)
                                        self.servo_on = []
				
		# Write Sensor Value
		if self.write_sens == 'ON':
			for id in self.id:
				data = []
				data_temp = self.rs.get_data(id)
				for temp in data_temp:
					data.append(temp)
				
				self._d_sensor.data = data
				OpenRTM_aist.setTimestamp(self._d_sensor)
				self._sensorOut.write()

		return RTC.RTC_OK
	
def RsServoManagerInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=rsservomanager_spec)
    manager.registerFactory(profile,
                            RsServoManager,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    RsServoManagerInit(manager)

    # Create a component
    comp = manager.createComponent("RsServoManager")

def main():
	mgr = OpenRTM_aist.Manager.init(sys.argv)
	mgr.setModuleInitProc(MyModuleInit)
	mgr.activateManager()
	mgr.runManager()

if __name__ == "__main__":
	main()

