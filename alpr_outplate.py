	

import gi
import numpy as np
import cv2
from openalpr import Alpr
import sys
import serial
import subprocess
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy
import json, ast
#from datetime import datetime


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ButtonWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ALPRS 0.2 Exit Cam")
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(250, 350)

        #hbox = Gtk.Box(spacing=100)
        #self.add(hbox)
        
        self.outter_box = Gtk.VBox(False,spacing=10)
        self.add(self.outter_box)
        
        hbox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        hbox.set_layout(Gtk.ButtonBoxStyle.CENTER) 
        self.outter_box.pack_start(hbox, False, True, 0)
        
        hbox.get_style_context().add_class("linked")

        button = Gtk.Button.new_with_mnemonic("_Close")
        hbox.add(button)
        button.connect("clicked", self.on_close_clicked)
        #hbox.pack_start(button, True, True, 0)
        
        button = Gtk.Button.new_with_mnemonic("Start the Engine")
        hbox.add(button)
        button.connect("clicked", self.on_button_clicked)
        #hbox.pack_start(button, True, True, 0)
        
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        self.outter_box.pack_end(hbox, False, True, 0)
        self.label_display = Gtk.Label("Output Log : ")
        hbox.add(self.label_display)
        
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        self.outter_box.pack_start(hbox, False, True, 0)
        self.status_log = Gtk.Label("Status : ")
        hbox.add(self.status_log)
        
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        self.outter_box.pack_end(hbox, False, True, 0)
        self.source_path = Gtk.Label("Status : ")
        hbox.add(self.source_path)
        
        #label_display.set_text("sdsd")
        
    def on_click_me_clicked(self, button):
		subprocess.Popen(["python", "allowed.py"])

    def on_button_clicked(self, button):
		
		arduino = serial.Serial('/dev/ttyACM1', 9600)
		command = str(85)
		arduino.write(command)
		#reachedPos = str(arduino.readline())
		
		#------
		# Use a service account
		cred = credentials.Certificate('./avmsystem-9811f-firebase-adminsdk-t24ce-47db31506e.json')
		firebase_admin.initialize_app(cred)

		db = firestore.client()
		
		arduino = serial.Serial('/dev/ttyACM0', 9600)
		command = str(85)
		arduino.write(command)
		#reachedPos = str(arduino.readline())
		
		RTSP_SOURCE  = 'rtsp://192.168.8.102:8080/h264_ulaw.sdp'
		WINDOW_NAME  = 'ALPR System 0.1'
		FRAME_SKIP   = 30
		self.source_path.set_text(str(RTSP_SOURCE))
		


		def open_cam_rtsp(uri):
			gst_str = ('rtspsrc location={} ! rtph264depay ! h264parse ! avdec_h264 ! '
               'videoconvert ! appsink').format(uri)
			return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)


		def main():
			alpr = Alpr('fr', 'fr.conf', '/usr/local/share/openalpr/runtime_data')
			if not alpr.is_loaded():
				print('Error loading OpenALPR')
				sys.exit(1)
			alpr.set_top_n(3)
			#alpr.set_default_region('new')

			cap = open_cam_rtsp(RTSP_SOURCE)
			if not cap.isOpened():
				alpr.unload()
				#sys.exit('Failed to open video file!')
				self.label_display.set_text("Output Log : Failed to open video file")
			#cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
			#cv2.setWindowTitle(WINDOW_NAME, 'Gate Camera test')
			#cv2.resizeWindow(WINDOW_NAME, 256, 256)

					
			#c.execute('create table pr1 (ID, Name, NP)')
			


			_frame_number = 0
			while True:
				ret_val, frame = cap.read()
				if not ret_val:
					self.label_display.set_text("Output Log : VidepCapture.read() failed. Exiting...")
					break

				_frame_number += 1
				if _frame_number % FRAME_SKIP != 0:
					continue
				#cv2.imshow(WINDOW_NAME, frame)
				#cv2.resizeWindow(WINDOW_NAME, frame, 256, 256)

				

				results = alpr.recognize_ndarray(frame)
				for i, plate in enumerate(results['results']):
					best_candidate = plate['candidates'][0]
					
					J = (u'{},'.format(best_candidate['plate'].upper(),best_candidate))
					print J
					
					plates_ref = db.collection(u'plates')
					arrayload = []
					
					for doc in plates_ref.stream():
					    payload = (u'{},'.format(doc.to_dict().get('plate')))
					    arrayload.append(payload)
					
					if J in arrayload:
						self.status_log.set_text(str(J))
						print("Matched")

						arduino = serial.Serial('/dev/ttyACM0', 9600)
						command = str(85)
						arduino.write(command)
						reachedPos = str(arduino.readline())
						
						logs_ref = db.collection(u'plates')
						
						J = (u'{}'.format(J))
						J = J.replace(',', '')
						print(J)
						
						user_id = logs_ref.where(u'plate', u'==', J).stream()
						for doc in user_id:
							print(u'{}'.format(doc.id))
							uName = (u'{},'.format(doc.to_dict().get('name')))
							
						now = firestore.SERVER_TIMESTAMP
						logz = db.collection('logs').document(doc.id).update({ 'timeexit' : (now)})
							#print(doc.id)
						print("------END---------")

					else:
						print("Doesn't Match")
						print(arrayload)
						



				if cv2.waitKey(1) == 27:
					break

			cv2.destroyAllWindows()
			cap.release()
			alpr.unload()








		if __name__ == "__main__":
			main()



    def on_open_clicked(self, button):
        print('"Open" button was clicked')

    def on_close_clicked(self, button):
        print("Closing application")
        Gtk.main_quit()


win = ButtonWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
