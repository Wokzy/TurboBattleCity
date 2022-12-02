from constants import *


def blit_grass(screen, gf):
	for obj in gf.grass:
		screen.blit(obj.image, obj.rect)


def blit_map(screen, gf, preview=[]):
	for obj in gf.map_objects:
		screen.blit(obj.image, obj.rect)


def blit_scores(screen, scores):
	for i in range(len(scores)):
		score_lenth_unit = (SCORE_FONT_SIZE)*(len(scores)*1.25 - 1)
		score_coords = (WIDTH // 2 - (score_lenth_unit // 2) - SCORE_FONT_SIZE*.5 + (SCORE_FONT_SIZE + SCORE_FONT_SIZE*0.85)*i, AVERAGE_MULTIPLYER)
		nick_coords = (score_coords[0]+(SCORE_FONT_SIZE - (NICK_FONT_SIZE*len(scores[i][2])))//4, score_coords[1] + SCORE_FONT_SIZE + AVERAGE_MULTIPLYER)
		screen.blit(scores[i][0], score_coords)
		screen.blit(scores[i][1], nick_coords)


def blit_runes(screen, gf): # gf.runes is list with dicts containing blit params
	for rune in gf.runes:
		screen.blit(rune['image'], rune['coords'])


def blit_bullets(screen, gf): # gf.bullets is list with objects
	for bullet in gf.bullets:
		screen.blit(bullet.image, bullet.rect)


def blit_additional_images(screen, imgs):
	for key in imgs:
		if type(imgs[key]) == list:
			for img in imgs[key]:
				screen.blit(img['image'], img['position'])
		elif type(imgs[key]) == dict:
			screen.blit(imgs[key]['image'], imgs[key]['position'])


def blit_additional_objects(screen, gf):
	for obj in gf.additional_objects:
		screen.blit(obj.image, obj.rect)


def blit_tanks(screen, tanks):
	for tank in tanks:
		blit_additional_images(screen, tanks[tank].additional_images)
		screen.blit(tanks[tank].image, tanks[tank].rect)
		blit_additional_images(screen, tanks[tank].top_additional_images)
		if tanks[tank].show_nickname:
			screen.blit(tanks[tank].nickname, (tanks[tank].rect.x, tanks[tank].rect.y - 8*AVERAGE_MULTIPLYER))


def blit_other_players(screen, gf):
	blit_tanks(screen, tanks=gf.players)


def blit_player(screen, gf):
	try:
		if gf.player != None:
			blit_additional_images(screen, gf.player.additional_images)
			screen.blit(gf.player.image, gf.player.rect)
			blit_additional_images(screen, gf.player.top_additional_images)
			if gf.player.show_nickname:
				screen.blit(gf.nickname, (gf.player.rect.x, gf.player.rect.y - 8*AVERAGE_MULTIPLYER))
	except Exception as e:
		print(e) #pass

