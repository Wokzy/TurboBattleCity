import pygame
from constants import *

'''
def prepare_object_to_sending(obj, split_data=False):
	if split_data:
		string = str(obj) + '\n'
	else:
		string = str(obj)
	return string.replace("'", '"').encode(ENCODING)
'''

def player_death():
	global controller
	if controller:
		controller.rumble(low_frequency=True, high_frequency=False, duration=525)

def event_handling(gf, main):
	global controller
	pressed_keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return 'quit'
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mos_pos = pygame.mouse.get_pos()
			for obj in gf.additional_objects:
				if obj.__class__.__name__ == 'Button' and obj.rect.collidepoint(mos_pos):
					obj.action(gf = gf, main = main)
					break
		#elif event.type == pygame.KEYDOWN:
			#if event.key == pygame.K_t and gf.player != None:
			#	gf.player.alive = False

	if gf.game_status == 1 and gf.player != None and gf.player.alive and gf.session_status == 'running':
		control_buttons_pressed = []
		control_axes = (0, 0)
		control_hat = (0, 0)

		if controller:
			if controller.get_numaxes() != 0:
				control_axes = (round(controller.get_axis(CONTROL_AXIS_INDEX*2)), -round(controller.get_axis(CONTROL_AXIS_INDEX*2+1)))
			if 'PS4' not in controller.get_name():
				control_hat = controller.get_hat(0)
			control_buttons_pressed = [c for c in range(0, controller.get_numbuttons()) if controller.get_button(c) != False]

		if (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]) or CONTROLLER_BOOST_BUTTON in control_buttons_pressed:
			gf.player.turn_on_boost()

		if pressed_keys[pygame.K_UP] or 1 in [control_hat[1], control_axes[1]]:
			gf.player.move(gf.map_objects, 'forward')
		elif pressed_keys[pygame.K_DOWN] or -1 in [control_hat[1], control_axes[1]]:
			gf.player.move(gf.map_objects, 'back')
		elif pressed_keys[pygame.K_RIGHT] or 1 in [control_hat[0], control_axes[0]]:
			gf.player.move(gf.map_objects, 'right')
		elif pressed_keys[pygame.K_LEFT] or -1 in [control_hat[0], control_axes[0]]:
			gf.player.move(gf.map_objects, 'left')

		if pressed_keys[pygame.K_SPACE] or CONTROLLER_SHOOT_BUTTON in control_buttons_pressed:
			if gf.player_ready_to_shoot():
				gf.shoot(gf.player)
		if pressed_keys[pygame.K_r] or CONTROLLER_RELOAD_BUTTON in control_buttons_pressed:
			gf.go_on_reload()


def init_devices():
	global controller
	pygame.joystick.init()

	try:
		controller = pygame.joystick.Joystick(0)
		print(controller.get_name(), ' is availible to use!')
	except:
		controller = None

	#print("Axes", (controller.get_numaxes()))
	#print("Balls", controller.get_numballs())
	#print("Buttons", controller.get_numbuttons())
	#print("Hats", controller.get_numhats())


#init_devices()

