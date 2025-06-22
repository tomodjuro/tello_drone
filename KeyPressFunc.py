import pygame

def init():
    pygame.init()
    #window initialization

def getKey(keyName):

    # variable for unpressed key
    answer = False

    # Only get event, do nothing
    for eve in pygame.event.get():pass

    # get all pressed keys
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        answer = True
    pygame.display.update()
    

    return answer



if __name__ == '__main__' :
    init()   