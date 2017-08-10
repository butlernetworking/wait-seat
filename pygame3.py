#!/usr/bin/python
import pygame
import RPi.GPIO as GPIO
import time

pygame.init()
TIMEVENT=25
pygame.time.set_timer(TIMEVENT, 1000)

LED_WAIT=23
LED_SEAT=24
LED_TVON=21
SW_TGL=16
TV_PWR=20

#set GPIO numbering mode and define input pin
GPIO.setmode(GPIO.BCM)

GPIO.setup(LED_WAIT,GPIO.OUT) # wait led, red
GPIO.setup(LED_SEAT,GPIO.OUT) # seat led, green
GPIO.setup(LED_TVON,GPIO.OUT) # tvon led, white ( and also feeds relay )
GPIO.setup(SW_TGL,GPIO.IN)	# seat wait toggle, push button
GPIO.setup(TV_PWR,GPIO.IN)	# mon power toggle, push button 

#start with tv power on
GPIO.output(LED_TVON,True)

#global donyet
donyet=False

resol = (1920,1080)
gdis = pygame.display.set_mode(resol)

wait = pygame.image.load('Pictures/pleasewait.jpg')
wait1 = pygame.image.load('Pictures/pleasewaity.jpg')
wait2 = pygame.image.load('Pictures/pleasewaitr.jpg')
seat = pygame.image.load('Pictures/logoseatyourselfg.jpg')

waitpic=1 # 1=yellow, 2=red
def togglepicture():
	global waitpic
	if waitpic==1:		
		# change it to red
		gdis.blit(wait2,(0,0))
		pygame.display.flip()
		waitpic=2
	else:
		# change it to yellow
		gdis.blit(wait1,(0,0))
		pygame.display.flip()
		waitpic=1

gdis.blit(seat, (00, 00))
pygame.display.flip()

WAIT=1
SEAT=0
seatingstate=SEAT
GPIO.output(LED_SEAT,True)
GPIO.output(LED_WAIT,False)

ON=1
OFF=0
tvpowerstate=ON
pygame.mouse.set_visible(False)

try:

	while not donyet:
		
		waitbutton=False
		seatbutton=False
		tvon=False
		tvoff=False
		
		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				donyet=True
			elif ev.type == pygame.KEYDOWN:
				if ev.key == pygame.K_3:
					waitbutton=True
				if ev.key == pygame.K_2:
					seatbutton=True
				if ev.key == pygame.K_1: # tv on
					tvon=True
				if ev.key == pygame.K_7: # tv off
					tvoff=True
				if ev.key == pygame.K_END:
					donyet=True
			elif ev.type == TIMEVENT:
				if seatingstate==WAIT:
					togglepicture()

		# check on button
		if GPIO.input(TV_PWR)==1:	# tv power toggle button was pressed
			if tvpowerstate==ON: # tv is on
				tvoff=True # get action 'if' to turn tv off
				pygame.time.wait(250)	# big debounce
			else: # tv is off
				tvon=True # get action 'if' to turn tv on
				pygame.time.wait(250)	# big debounce
			
		# check seat-wait button
		if GPIO.input(SW_TGL)==1:	# set seat / wait toggle was pressed 
			if seatingstate==SEAT:
				waitbutton=True
				pygame.time.wait(250)	# big debounce
			else:
				seatbutton=True 
				pygame.time.wait(250)	# big debounce

			#figure what to do
		if tvon==True: # turn on was requested
			if tvpowerstate==OFF:
				#GPIO.output(TV_PWR,False) # active low
				GPIO.output(LED_TVON,True)
				tvpowerstate=ON
		
		if tvoff==True: # turn off was requested
			if tvpowerstate==ON:
				#GPIO.output(TV_PWR,True) # active low
				GPIO.output(LED_TVON,False)
				tvpowerstate=OFF

		if waitbutton==True:
			if seatingstate==SEAT: # currently off, seat yourself				
				seatingstate=WAIT # turn it on, change to wait
				GPIO.output(LED_WAIT,True)
				GPIO.output(LED_SEAT,False)
				gdis.blit(wait1,(0,0))
				pygame.display.flip()
		 
		if seatbutton==True:
			if seatingstate==WAIT: # currently on, please wait to be seated				
				seatingstate=SEAT # turn it off, seat yourself
				GPIO.output(LED_SEAT,True)
				GPIO.output(LED_WAIT,False)
				gdis.blit(seat,(0,0))
				pygame.display.flip()					
					
					
finally:
	GPIO.output(LED_TVON,False)
	#GPIO.output(TV_PWR,True) #tv off (active low)
	GPIO.cleanup()
	pygame.mouse.set_visible(True)
