import random, sys, pygame, time, copy
import numpy as np
from pygame.locals import *
from CLASS_TERMINEE import *


#Activate tick and music for Normal Mode
FPS = 10 # frames per second to update the screen
WINDOWWIDTH = 720 # width of the program's window, in pixels
WINDOWHEIGHT = 480 # height in pixels
SPACESIZE = 40 # width & height of each space on the board, in pixels
BOARDWIDTH = 11 # how many columns of spaces on the game board
BOARDHEIGHT = 11 # how many rows of spaces on the game board
CARDS_TILE=[str(i) for i in range(13)] # L'as est codé avec un 0, le 2 avec un 12
WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value
HINT_TILE = 'HINT_TILE' # an arbitrary but unique value
MODE_PLAY='MODE_PLAY'# an arbitrary but unique value
MODE_ML='MODE_ML'# an arbitrary but unique value
OPTIONS=['HIT','STAND','SPLIT','DOUBLE','DEAL'] #Differents moove possible
DECK_OF_CARDS=6 #Number of decks in the dealer's card shoe
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation


# Amount of space on the left & right side (XMARGIN) or above and below
# (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#              R    G    B
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
TEXTBGCOLOR3=BROWN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN

# Global Variables :

#enterMode_ML: if True then the game enter in auto mode and doesn't ask 
#to select the mode between each games

#for DATA collecting: 
#Matrix_DATA_ML1 for the strategy DATA (used in Random Forest)
#Matrix_DATA_ML2 for the bets DATA (used for Statistics)


enterMode_ML=[False]

Matrix_DATA_ML1=[[0],["DEAL"],["LAST_CO"],["LAST_CH"],["GAIN"]]
Matrix_DATA_ML2=[["TRUECOUNT"],["BET_AMOUNT"],["GAIN"]] 


#Main loop 
def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE
    pygame.mixer.pre_init(44100, -16, 2, 2048) 
    pygame.init()
    
    #Initiate the clock and the windows
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    
    #Caption of the window
    pygame.display.set_caption('BlackJack Ensae garanti 100% fait maison')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    # Set up the background image.
    boardImage1 = pygame.image.load('ALL_FILES/blackjack-wall.jpg')
    # Use smoothscale() to stretch the board image to fit the entire board:
    boardImage1 = pygame.transform.smoothscale(boardImage1, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    boardImageRect1 = boardImage1.get_rect()
    boardImageRect1.topleft = (XMARGIN, YMARGIN)
    BGIMAGE = pygame.image.load('ALL_FILES/black.jpg')
    # Use smoothscale() to stretch the background image to fit the entire window:
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    #Add the background on top of that
    BGIMAGE.blit(boardImage1, boardImageRect1)
    
    global sabot,Truecount,cash_players 
    sabot=getNewSabot() #initiate the shoe with the 6 decks of cards
    Truecount=[0,0,0] #initial energy or truecount (full details in pdf document)
    cash_players=[1000,1000,1000,0] #initial cash for each player and dealer
    
    # Run the main game.
    while True:
        if runGame(enterMode_ML,Matrix_DATA_ML1,Matrix_DATA_ML2) == False:
            pygame.quit()
            sys.exit()
            
        
def runGame(ML_mode,Matrix_DATA1,Matrix_DATA2):
    # Plays a single game of reversi each time this function is called.

    # Reset the board and game.
    count_loop_ML=0 #used to count moove that has been selected 
    
    #Initiate a 11*11 empty board which will contains the cards of each player
    mainBoard = getNewBoard()  
    bets=[[0,0] for i in range(3)] #initiate the bets to 0
    
    #reset board between each game and distribute a card for the dealer
    resetBoard(mainBoard,sabot,Truecount) 
    showHints = False #Hints desactivated
    turn = 1 #begin with player1
    pile=1 #begin with pile1 (pile is always 1 if player hasn't splitted his cards)
    selected_data=[] #used to collect data properly

    # Draw the starting board
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())
    
    #Ask which mode the player wants to play and proceed only if not autoMode
    if ML_mode[-1]==False:
        mode=enterMode()
        if mode==MODE_ML:
            ML_mode.pop(0)
            ML_mode.append(True)
    else:
        mode=MODE_ML
        
        
    #Display the green table, the cards , the cash , the count
    drawBoard(mainBoard,turn,bets,cash_players)
    if ML_mode==[True]:
        
        boardImage2 = pygame.image.load('ALL_FILES/VRAIBOARD.png')
        boardImage2 = pygame.transform.smoothscale(boardImage2, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
        boardImageRect2 = boardImage2.get_rect()
        boardImageRect2.topleft = (XMARGIN, YMARGIN)
    else:
        boardImage2 = pygame.image.load('ALL_FILES/VRAIBOARD2.png')
        boardImage2 = pygame.transform.smoothscale(boardImage2, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
        boardImageRect2 = boardImage2.get_rect()
        boardImageRect2.topleft = (XMARGIN, YMARGIN)
    BGIMAGE.blit(boardImage2, boardImageRect2)
    if mode!=MODE_ML:
        playmusic2( "ALL_FILES/Casino-Ambiance.ogg", 1)  #Play music of main game
    computer_can_move=False #computer_can move will be true if second round of table
    
    # Make the Surface and Rect objects for the "New Game" and "Hints" buttons
    # Make the Surface and Rect objects for the BETS and MOOVE buttons
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR2)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)
    hintsSurf = FONT.render('Hints', True, TEXTCOLOR, TEXTBGCOLOR2)
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (WINDOWWIDTH - 8, 40)
    BetSurf = FONT.render('Mises', True, TEXTCOLOR, TEXTBGCOLOR2)
    BetRect = BetSurf.get_rect()
    BetRect.topleft = (2, 10)
    Deal_Surf=pygame.transform.smoothscale(IM_DEAL,(2*SPACESIZE,SPACESIZE))
    Deal_Rect=Deal_Surf.get_rect()
    Stand_Surf=pygame.transform.smoothscale(IM_STAND,(2*SPACESIZE,SPACESIZE))
    Stand_Rect=Stand_Surf.get_rect()
    Hit_Surf=pygame.transform.smoothscale(IM_HIT,(2*SPACESIZE,SPACESIZE))
    Hit_Rect=Hit_Surf.get_rect()
    Stand_Surf=pygame.transform.smoothscale(IM_STAND,(2*SPACESIZE,SPACESIZE))
    Stand_Rect=Stand_Surf.get_rect()
    Double_Surf=pygame.transform.smoothscale(IM_DOUBLE,(2*SPACESIZE,SPACESIZE))
    Double_Rect=Double_Surf.get_rect()
    Split_Surf=pygame.transform.smoothscale(IM_SPLIT,(2*SPACESIZE,SPACESIZE))
    Split_Rect=Split_Surf.get_rect()
    bet_5_Surf=pygame.transform.smoothscale(IM_BET5.convert_alpha(),(2*SPACESIZE,2*SPACESIZE))
    bet_25_Surf=pygame.transform.smoothscale(IM_BET25.convert_alpha(),(2*SPACESIZE,2*SPACESIZE))
    bet_50_Surf=pygame.transform.smoothscale(IM_BET50.convert_alpha(),(2*SPACESIZE,2*SPACESIZE))
    bet_100_Surf=pygame.transform.smoothscale(IM_BET100.convert_alpha(),(2*SPACESIZE,2*SPACESIZE))
    bet_5_Rect = bet_5_Surf.get_rect()
    bet_25_Rect = bet_25_Surf.get_rect()
    bet_50_Rect = bet_50_Surf.get_rect()
    bet_100_Rect = bet_100_Surf.get_rect()
    Deal_Rect.topleft=(BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN,5*YMARGIN)
    Hit_Rect.topleft=(BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN,8*YMARGIN)
    Stand_Rect.topleft=(BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN,11*YMARGIN)
    Double_Rect.topleft=(BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN,14*YMARGIN)
    Split_Rect.topleft=(BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN,17*YMARGIN)
    bet_5_Rect.topleft = (0.1*XMARGIN, 4*YMARGIN)
    bet_25_Rect.topleft = (0.1*XMARGIN, 8*YMARGIN)
    bet_50_Rect.topleft = (0.1*XMARGIN, 12*YMARGIN)
    bet_100_Rect.topleft = (0.1*XMARGIN, 16*YMARGIN)



    
    # main game loop
    while True:
        # Keep looping for player and computer's turns.
        
        move_choice = None
        bet_choice=None
        
        if mode==MODE_PLAY:  
            
            #Keep looping until valid moove is selected
            while move_choice == None and bet_choice==None:
                # Keep looping until the player clicks on a valid space.
                
                boardToDraw = mainBoard
                betscopy=bets
                checkForQuit() #If player quit the game the game close properly
                
                for event in pygame.event.get(): # Handle mouse click events
                    if event.type == MOUSEBUTTONUP:
                        
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint( (mousex, mousey) ):
                            # Start a new game
                            return True
                            
                        elif hintsRect.collidepoint( (mousex, mousey) ):
                            # Toggle hints mode
                            showHints = not showHints
                        # movexy is set to a two-item tuple XY coordinate, or None value
                        
                        #Return which button has been selected
                        move_choice = get_decision(mousex, mousey)
                        bet_choice,bet_amount=get_betchoice(mousex,mousey)
                        
                        if bet_choice!= None:
                            bet_choice_sauv,bet_amount_sauv=bet_choice,bet_amount
                        
                        if move_choice != None and not isValidMove(boardToDraw, turn, pile, move_choice,betscopy) :
                            
                            move_choice = None
                            
                        if bet_choice!=None and not isValid_to_bet(boardToDraw):
                            bet_choice=None
                
                #Keep displaying the games elements
                drawBoard(boardToDraw,turn,betscopy,cash_players)
                DISPLAYSURF.blit(newGameSurf, newGameRect)
                DISPLAYSURF.blit(hintsSurf, hintsRect)
                DISPLAYSURF.blit(BetSurf, BetRect)
                DISPLAYSURF.blit(Deal_Surf,Deal_Rect)
                DISPLAYSURF.blit(Stand_Surf,Stand_Rect)
                DISPLAYSURF.blit(Hit_Surf,Hit_Rect)
                DISPLAYSURF.blit(Double_Surf,Double_Rect)
                DISPLAYSURF.blit(Split_Surf,Split_Rect)
                DISPLAYSURF.blit(bet_5_Surf,bet_5_Rect)
                DISPLAYSURF.blit(bet_25_Surf,bet_25_Rect)
                DISPLAYSURF.blit(bet_50_Surf,bet_50_Rect)
                DISPLAYSURF.blit(bet_100_Surf,bet_100_Rect)
        
                pygame.display.update()
                
        else: #IF ML/AUTO MODE HAS BEEN SELECTED
            for event in pygame.event.get(): # Handle mouse click events
                    if event.type == MOUSEBUTTONUP:
                        
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint( (mousex, mousey) ):
                            # Start a new game
                            return True
            boardToDraw = mainBoard
            betscopy=bets
            checkForQuit()
            getRandomValidMove(boardToDraw,count_loop_ML,turn,pile,betscopy,Truecount)
            #countloop= 0 2 4 are corresponds to a bets that has to selected (wa are in automode)
            #countloop= 1 3 5 corresponds to a deal moove (bets are placed in front of the players)
            #countloop>=6 corresponds to the rest of the moove of the game
            if count_loop_ML in [0,2,4]: 
                #Return the moove determined by Random Forest method
                bet_choice_sauv,bet_amount_sauv=getRandomValidMove(boardToDraw,count_loop_ML,turn,pile,betscopy,Truecount)
                #if turn==2 or turn==3 or turn==1:
                      #Collect the data for Random Forest
                      #Matrix_DATA2[0].append(Truecount[2])
                      #Matrix_DATA2[1].append(bet_amount_sauv)
                    
                    
            else:
                move_choice=getRandomValidMove(boardToDraw,count_loop_ML,turn,pile,betscopy,Truecount)
            
            # Draw the game board with cards distributed
            drawBoard(boardToDraw,turn,betscopy,cash_players)
            if mode==MODE_PLAY:
                pauseUntil = time.time() + random.randint(5, 15) * 0.01
                while time.time() < pauseUntil:
                    pygame.display.update()
            
    
            # Draw the "New Game" & "Hints" + Bets and Choices buttons
            
            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(hintsSurf, hintsRect)
            DISPLAYSURF.blit(BetSurf, BetRect)
            DISPLAYSURF.blit(Deal_Surf,Deal_Rect)
            DISPLAYSURF.blit(Stand_Surf,Stand_Rect)
            DISPLAYSURF.blit(Hit_Surf,Hit_Rect)
            DISPLAYSURF.blit(Double_Surf,Double_Rect)
            DISPLAYSURF.blit(Split_Surf,Split_Rect)
            DISPLAYSURF.blit(bet_5_Surf,bet_5_Rect)
            DISPLAYSURF.blit(bet_25_Surf,bet_25_Rect)
            DISPLAYSURF.blit(bet_50_Surf,bet_50_Rect)
            DISPLAYSURF.blit(bet_100_Surf,bet_100_Rect)
    
            
            pygame.display.update()
            
            count_loop_ML+=1 #update count of Moves that have been selected
            
            
            
            
            
        # Leaving the move_choice / bet_choice loop
        
        # Now we have to make the move to proper player and end the turn:
            
        #If it's player's turn:  ( player turn =1,2,3 / dealer=4)
        if turn<=3:
            #Note that we know the player has just done a move or a valid bet
            
            
            #Verify is the move is possible and make it
            if isValidMove(boardToDraw, turn, pile, move_choice,betscopy):
                
                #Make the valid move and update the board
                makeMove(boardToDraw,move_choice,turn,sabot,pile,betscopy,bet_amount_sauv,cash_players,Truecount)
                
                #UPDATE PILE AND TURN and DATA_Matrix for each mooves
                if move_choice=='STAND':
                    if has_splitted(boardToDraw,turn):
                        
                        
                        if pile==1:
                            pile=2
                        else:
                            pile=1
                            turn+=1
                    else:
                        card_dealer=get_card_dealer(boardToDraw)
                        last_count_player=get_last_count(boardToDraw,turn,betscopy,True)
                        #if last_count_player!=None:
                            #DATA_LINE=[Matrix_DATA1[0][-1]+1,card_dealer,last_count_player,'STAND',0]
                            #for i in range(len( DATA_LINE)):
                                #Matrix_DATA1[i].append(DATA_LINE[i])
                                
                            #selected_data.append(turn)
                        turn+=1
                        
                        
                    
                elif move_choice=='DOUBLE':
                    card_dealer=get_card_dealer(boardToDraw)
                    last_count_player=get_last_count(boardToDraw,turn,betscopy,False)
                    #if last_count_player!=None:
                        
                        #DATA_LINE=[Matrix_DATA1[0][-1]+1,card_dealer,last_count_player,'DOUBLE',turn]
                        #for i in range(len( DATA_LINE)):
                            #Matrix_DATA1[i].append(DATA_LINE[i])
                        #selected_data.append(turn)
                    if not has_splitted(boardToDraw,turn):
                        turn+=1
                    else:
                        if pile==1:
                            pile=2
                        else:
                            turn+=1
                            pile=1
                    
                
                
                elif move_choice=='DEAL':
                    turn+=1
                    playmusic1( "ALL_FILES/sound_bet.ogg", 1) 
                    
                    
                elif move_choice=='HIT':
                    
                    card_dealer=get_card_dealer(boardToDraw)
                    last_count_player=get_last_count(boardToDraw,turn,betscopy,False)
                    #if last_count_player!=None:
                        #if Matrix_DATA1[3][-1]!='HIT' or turn!=Matrix_DATA1[4][-1]:
                            #DATA_LINE=[Matrix_DATA1[0][-1]+1,card_dealer,last_count_player,'HIT',turn]
                            #for i in range(len( DATA_LINE)):
                                #Matrix_DATA1[i].append(DATA_LINE[i])
                            #selected_data.append(turn)
                        #else:
                            #for i in range(5):
                                #Matrix_DATA1[i].pop(-1)
                            #selected_data.pop(-1)
                                
                            #DATA_LINE=[Matrix_DATA1[0][-1]+1,card_dealer,last_count_player,'HIT',turn]
                            #for i in range(len( DATA_LINE)):
                                #Matrix_DATA1[i].append(DATA_LINE[i])
                            #selected_data.append(turn)
                            
                    convert__values=convertBoard(boardToDraw)
                    card_allplayers , ace_allpos = get_cardplayers(convert__values)
                    card_player=card_allplayers[2*(turn-1)+pile-1]
                    if not has_splitted(boardToDraw,turn):
                        if getValidMoves(boardToDraw, turn,pile,betscopy)==[]:
                        
                            turn+=1
                        
                        elif card_player[6]!=0:
                            pile+=1
    
                        
                    else:
                        if getValidMoves(boardToDraw, turn,pile,betscopy)==[]:
                            if pile==1:
                                pile=2
                            else:
                                pile=1
                                turn+=1
                        elif card_player[6]!=0:
                        
                            if pile==1:
                                pile=2
                            else:
                                pile=1
                                turn+=1
                        
                
                
            
            #If bets has been selected (no moove)
            else:
                
                makeMove(boardToDraw,bet_choice_sauv,turn,sabot,pile,betscopy,bet_amount_sauv,cash_players,Truecount)
                
            pygame.display.update()
                
            
                
        #Turn of dealer
        if turn==4: 
            
            # Draw the board.
            drawBoard(boardToDraw,turn,betscopy,cash_players)
            #drawInfo(mainBoard, playerTile, computerTile, turn)
            # Draw the "New Game" and "Hints" buttons.
            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(hintsSurf, hintsRect)

            # Make it look like the computer is thinking by pausing a bit
            if mode!=MODE_ML:
                pauseUntil = time.time() + random.randint(5, 15) * 0.1
                while time.time() < pauseUntil:
                    pygame.display.update()

            # Make the move and end the turn.
            
             
            
            
            #If it's the second tour of table then computer can move is True 
            
            
            if computer_can_move:
                while True:
                    choice_computer = getComputerMove(boardToDraw,turn,pile,betscopy)
                    
                    #If deaker has just stand update the bets , get Results, make win bets and update the DATA for Random Forest
                    if choice_computer[0]=='STAND':
                        Results_=getResults(boardToDraw,cash_players,betscopy)
                        
                        selected_Results_DATA=[Results_[i-1][0] for i in selected_data]
                        selected_Bets_DATA=[betscopy[i-1][0] for i in selected_data]
                        
                        
                        
                        m=len(selected_Results_DATA)
                        #for i in range(m):
                            #bets_selected=selected_Bets_DATA[i]
                        
                            #results_selected=selected_Results_DATA[i]
                            #if results_selected=='BLACKJACK':
                               #Matrix_DATA1[4][-m+i]=bets_selected*2
                               
                               
                            #elif  results_selected=='WIN':
                                #Matrix_DATA1[4][-m+i]=bets_selected
                            #elif results_selected=='TIE':
                                 #Matrix_DATA1[4][-m+i]=0
                            #else:
                                #Matrix_DATA1[4][-m+i]=-bets_selected
                        #for i in range(1,3):
                            #for j in range(2):
                                #if Results_[i][j]=='BLACKJACK':
                                    #Matrix_DATA2[3].append()
                                    
                        
                        
                        print("Truecount=",Truecount)    
                        #Make win respective amount of each player
                        MakeWinBets(boardToDraw,cash_players,betscopy,Matrix_DATA2)
                        
                        break
                        #Exit the loop
                        
                    #If the dealer continue to play and didn't stand    
                    makeMove(boardToDraw,choice_computer[0],turn,sabot,1,betscopy,bet_amount_sauv,cash_players,Truecount)
                    drawBoard(boardToDraw,turn,betscopy,cash_players)
                    pygame.display.update()
                    
                    
              
                    drawBoard(boardToDraw,turn,betscopy,cash_players)
                    
                    
                    
                break # Display the menu of the end , ask the player "Play again?"
                
            #if computer can moove was False then computer can Move become True
            #which indicate the second round of table and reset the second round of table 
            #with turn=1
            turn=1
            
            computer_can_move=True
            
                
                # Only set for the player's turn if they can make a move.
        
        mainBoard=boardToDraw

    # Display the final score.
    drawBoard(mainBoard,turn,betscopy,cash_players,True)
    

    # Determine the text of the message to display.

    
    text="Python-Blackjack"
               
    

    textSurf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)-2*SPACESIZE)
    

    # Display the "Play again?" text with Yes and No buttons.
    text2Surf = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50-2*SPACESIZE)

    # Make "Yes" button.
    yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90-2*SPACESIZE)

    # Make "No" button.
    noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
    noRect = noSurf.get_rect()
    noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90-2*SPACESIZE)
    if mode==MODE_PLAY:
        while True:
            # Process events until the user clicks on Yes or No.
            checkForQuit()
            for event in pygame.event.get(): # event handling loop
                if event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    if yesRect.collidepoint( (mousex, mousey) ):
                        return True
                    elif noRect.collidepoint( (mousex, mousey) ):
                        return False
            DISPLAYSURF.blit(textSurf, textRect)
            DISPLAYSURF.blit(text2Surf, text2Rect)
            DISPLAYSURF.blit(yesSurf, yesRect)
            DISPLAYSURF.blit(noSurf, noRect)
            pygame.display.update()
            
    else:
        
        return True


        
        
        
        
        
#FUNCTIONS  
        
def playmusic1( musique, loop):   
    
    # Read music on first Channel 
    pygame.mixer.music.load(musique)
    pygame.mixer.Channel(0).play(pygame.mixer.Sound(musique))
def playmusic2( musique,loop):
    # Read music on second Channel 
    pygame.mixer.Channel(1).play(pygame.mixer.Sound(musique))
    
    
#Check if one splayer has just splitted  
def has_splitted(board,player_turn):
    convert_cards=convertBoard (board)
    matrix_value,aces=get_cardplayers(convert_cards)
    if matrix_value[2*(player_turn)-1][0]!=0:
        return True
    return False
    

#If booleen = False : Convert indices of row and col (of board) to the exact coordonate in a 11*11 grid
#If booleen=True : Convert indice of row and col (of board) to their positions where they will be displayed
def translateBoardToPixelCoord(x, y,booleen):
    if booleen==False:
        return XMARGIN + y * SPACESIZE + int(SPACESIZE / 2), YMARGIN + x * SPACESIZE + int(SPACESIZE / 2)
    if x==0 or x==1:
        return XMARGIN+11*(SPACESIZE / 2)+y*(SPACESIZE/13),YMARGIN+(SPACESIZE/2)+y*(SPACESIZE/3)
    if y==BOARDHEIGHT-1 or y==BOARDHEIGHT-2:
        return XMARGIN+9*SPACESIZE+(x-2)*(SPACESIZE/13)+(BOARDHEIGHT-1-y)*SPACESIZE*1.2, YMARGIN+6.6*SPACESIZE-(x-2)*(SPACESIZE/3)
    if y==0 or y==1:
        return XMARGIN+2*SPACESIZE+(x-2)*(SPACESIZE/13)+y*SPACESIZE*1.2, YMARGIN+6.6*SPACESIZE-(x-2)*(SPACESIZE/3)
    if x==BOARDWIDTH-1 or x==BOARDWIDTH-2:
        return XMARGIN+5.5*SPACESIZE+(y-2)*(SPACESIZE/13)+(BOARDWIDTH-1-x)*SPACESIZE*1.2, YMARGIN+7.8*SPACESIZE-(y-2)*(SPACESIZE/3)
    return XMARGIN + y * SPACESIZE + int(SPACESIZE / 2), YMARGIN + x * SPACESIZE + int(SPACESIZE / 2)

#Return a RandomValidMove to collect data
def getRandomValidMove(boardgame,compteur_turn,turn_player,turn_pile,bets_player,True_count):
    bet_choices=[]
    #On se débrouille pour que les moyennes de mises soit les mêmes pour pouvoir comparer les strat
    #Le notebook stratemises donnait 19 pour la moyenne de la stratégie ML avec mises , on 
    #essaie donc de donner la meme moyenne de mises aux deux autres stratégies
    
    
    if compteur_turn in [0,2,4]:
        if turn_player==1 or turn_player==2:
            return ('bet25',19.78)
        else:
            if True_count[-1]<=0:
                return ('bet5',5)
            if True_count[-1] in [1,2]:
                return ('bet25',25)
            if True_count[-1]==3:
                return ('bet50',50)
            if True_count[-1]>=4:
                return ('bet100',100)
            return ('bet25',25)
            
    
        
        
        
        
        
        
        
    else:
        if turn_player==1:  #Used for optimal strategy of blackjack (desactivated)
            if bets_player[turn_player-1][0]==0:
                return 'DEAL'
            stateP, stateD =get_count(boardgame,turn_player,turn_pile,bets_player)
            
            has_split=(bets_player[turn_player-1][1]!=0)
            if stateP=='A-A':
                if has_split:
                    return 'HIT'
                return 'SPLIT'
            elif stateP in ['2','3','4','5','6','7','8']:
                return 'HIT'
            elif stateP=='9':
                if stateD in  ['3','4','5','6']:
                    return 'DOUBLE'
                return 'HIT'
            elif stateP=='10':
                if stateD not in ['10','A']:
                    return 'DOUBLE'
                return 'HIT'
            elif stateP=='11':
                if stateD!='A':
                    return 'DOUBLE'
                return 'HIT'
            elif stateP=='12':
                if stateD in ['4','5','6']:
                    return 'STAND'
                return 'HIT'
            elif stateP in ['13','14','15','16']:
                if stateD in ['2','3','4','5','6']:
                    return 'STAND'
                return 'HIT'
            elif stateP in ['17','18','19','20','21']:
                return 'STAND'
            elif stateP in ['A-2','A-3','A-4','A-5','A-6']   :
                return 'HIT'
            elif stateP=='A-7':
                if stateD in ['9','10','A']:
                    return 'HIT'
                return 'STAND'
            elif stateP in ['A-8','A-9','A-10']:
                return 'STAND'
            elif stateP in ['2-2','3-3']:
                if has_split:
                    return 'HIT'
                else:
                    if stateD in['8','9','10','A']:
                        return 'HIT'
                    return 'SPLIT'
            elif stateP=='4-4':
                if has_split:
                    return 'HIT'
                else:
                    if stateD in ['5','6']:
                        return 'SPLIT'
                    return 'HIT'
            elif stateP=='5-5':
                if has_split:
                    if stateD not in ['10','A']:
                        return 'DOUBLE'
                    return 'HIT'
                else:
                    if stateD in ['10','A']:
                        return 'HIT'
                    return 'SPLIT'
            elif stateP in ['6-6','7-7']:
                if has_split:
                    if stateD in ['3','4','5','6']:
                        return 'STAND'
                    return 'HIT'
                    
                if stateD in ['9','10','A']:
                    return 'HIT'
                return 'SPLIT'
            elif stateP=='8-8':
                if has_split:
                    if stateD in ['2','3','4','5','6']:
                        return 'STAND'
                    return 'HIT'
                else:
                    return 'SPLIT'
            elif stateP=='9-9':
                if has_split:
                    return 'STAND'
                else:
                    if stateD in ['7','10','A']:
                        return 'STAND'
                    return 'SPLIT'
            elif stateP=='10-10':
                return 'STAND'
            elif stateP=='A-0':
                return 'HIT'
        else: #RANDOM FOREST STRATEGY
            if bets_player[turn_player-1][0]==0:
                return 'DEAL'
            stateP, stateD =get_count(boardgame,turn_player,turn_pile,bets_player)
            
            has_split=(bets_player[turn_player-1][1]!=0)
            if stateP=='A-A':
                if has_split:
                    return 'HIT'
                return 'SPLIT'
            elif stateP in ['2','3','4','5','6','7','8']:
                if stateP=='7' and stateD=='3':
                    return 'STAND'
                
                return 'HIT'
            elif stateP=='9':
                if stateD in  ['3','4','5','7','9']:
                    return 'DOUBLE'
                return 'HIT'
                
            elif stateP=='10':
                if stateD=='A' or stateD=='10':
                    return 'HIT'
                return 'DOUBLE'
                
            elif stateP=='11':
                if stateD=='A' or stateD=='10' or stateD=='2':
                    return 'HIT'
                return 'DOUBLE'
            elif stateP=='12':
                if stateD =='4':
                    return 'STAND'
                return 'HIT'
            elif stateP=='13':
                if stateD in ['3','4','5','6']:
                    return 'STAND'
                return 'HIT'
            elif stateP =='14':
                if stateD in ['2','3','4','5','6']:
                    return 'STAND'
                return 'HIT'
            elif stateP =='15':
                if stateD in ['2','3','4','5','6','8']:
                    return 'STAND'
                return 'HIT'
            elif stateP =='16':
                if stateD in ['2','3','4','5','7']:
                    return 'STAND'
                return 'HIT'
            elif stateP in ['17','18','19','20','21']:
                return 'STAND'
            elif stateP in ['A-2','A-3','A-4','A-5']   :
                return 'HIT'
            elif stateP=='A-6':
                if stateD=='3' or stateD=='4':
                    return 'STAND'
                return 'HIT'
                
            elif stateP=='A-7':
                if stateD in ['A']:
                    return 'HIT'
                return 'STAND'
            elif stateP=='A-8':
                if stateD in ['5','6','7']:
                    return 'DOUBLE'
                return 'STAND'
            elif stateP=='A-9':
                if stateD =='2':
                    return 'HIT'
                return 'STAND'
            elif stateP =='A-10':
                return 'STAND'
            elif stateP in ['2-2','3-3']:
                if has_split:
                    return 'HIT'
                else:
                    if stateD in['8','9','10','A']:
                        return 'HIT'
                    return 'SPLIT'
            elif stateP=='4-4':
                if has_split:
                    return 'HIT'
                else:
                    if stateD in ['5','6']:
                        return 'SPLIT'
                    return 'HIT'
            elif stateP=='5-5':
                if has_split:
                    if stateD not in ['10','A']:
                        return 'DOUBLE'
                    return 'HIT'
                else:
                    if stateD in ['10','A']:
                        return 'HIT'
                    return 'SPLIT'
            elif stateP in ['6-6','7-7']:
                if has_split:
                    if stateD in ['3','4','5','6']:
                        return 'STAND'
                    return 'HIT'
                    
                if stateD in ['9','10','A']:
                    return 'HIT'
                return 'SPLIT'
            elif stateP=='8-8':
                if has_split:
                    if stateD in ['2','3','4','5','6']:
                        return 'STAND'
                    return 'HIT'
                else:
                    return 'SPLIT'
            elif stateP=='9-9':
                if has_split:
                    return 'STAND'
                else:
                    if stateD in ['7','10','A']:
                        return 'STAND'
                    return 'SPLIT'
            elif stateP=='10-10':
                return 'STAND'
            elif stateP=='A-0':
                return 'HIT'
            
            
                
                    
                    
#Get the basic strategy "states" (les différentes combinaison de cartes sur la STRATEGIE DE BASE AU BLACKJACK)
def get_count(boardplay,turn_players,turn_piles,bets_players):
    convert__values=convertBoard(boardplay)
    card_allplayers , ace_allpos = get_cardplayers(convert__values)
    card_player=card_allplayers[2*(turn_players-1)+turn_piles-1]
    non_aces=[i for i in card_player if i!=1]
    aces=[i for i in card_player if i==1]
    ace_player=ace_allpos[turn_players-1][turn_piles-1]
    countmin=sum(card_player)
    countmin_nonaces=sum(non_aces)
    card_dealer=str(card_allplayers[6][0])
    if card_dealer=='1':
        card_dealer='A'
    if 1 in card_player:
        
        if card_player[0]==1 and card_player[1]==1:
            if turn_piles==1:
                if card_player[2]==0:
                    return 'A-A',card_dealer
                else:
                    if True in [countmin+10*i==20 for i in range(ace_player+1)]:
                        return '20',card_dealer
                    elif True in [countmin+10*i==21 for i in range(ace_player+1)]:
                        return '21',card_dealer
                    else:
                        return str(countmin),card_dealer
                    
            else:
                if True in [countmin+10*i==20 for i in range(ace_player+1)]:
                        return '20',card_dealer
                elif True in [countmin+10*i==21 for i in range(ace_player+1)]:
                    return '21',card_dealer
                else:
                    return str(countmin),card_dealer
        elif len(aces)>=2:
            if True in [countmin+10*i==20 for i in range(ace_player+1)]:
                        return '20',card_dealer
            elif True in [countmin+10*i==21 for i in range(ace_player+1)]:
                return '21',card_dealer
            else:
                return str(countmin),card_dealer
        elif len(aces)==1:
            if countmin_nonaces<=10:
                return 'A-'+str(countmin_nonaces),card_dealer
            else :
                return str(countmin),card_dealer
    else:
        if card_player[0]==card_player[1]:
            if card_player[2]==0:
                
                
                return str(card_player[0])+'-'+str(card_player[0]),card_dealer
            else:
                return str(countmin),card_dealer
        else:
            return str(countmin),card_dealer
    
                
#Convert the last card index on a list to is coordonate on a 11*11 grill
# ( Used for initial Display but we have been doing some modifications )
def convertPosList_to_Board(i,turn_player)   :
    if turn_player==1:
        return (i+2,BOARDWIDTH-1)
    elif turn_player==2:
        return (BOARDHEIGHT-1,i+2)
    elif turn_player==3:
        return (i+2,0)
     
        
        
        
#Reset the shoe of cards with 6 deck and shuffle the cards
def getNewSabot():
    NEW_SABOT=[]
    for j in range(DECK_OF_CARDS):
        for i in CARDS_TILE:
            for k in range(4):
                NEW_SABOT.append(i)
    
    random.shuffle(NEW_SABOT)
    return NEW_SABOT

#Reset the shoue , shuffle cards and reset Truecount
def resetSabot(PREVIOUS_SABOT,PREVIOUS_TRUECOUNT):
    for j in range(DECK_OF_CARDS):
        for i in CARDS_TILE:
            for k in range(4):
                PREVIOUS_SABOT.append(i)
    
    random.shuffle(PREVIOUS_SABOT)
    PREVIOUS_TRUECOUNT[0]=0
    PREVIOUS_TRUECOUNT[1]=0
    PREVIOUS_TRUECOUNT[2]=0
    
   
#Check if the shoe is empty after each moove    
def checkforsabot_empty(PREVIOUS_SABOT,PREVIOUS_TRUECOUNT):
    if len(PREVIOUS_SABOT)==0:
        print("SABOT VIDE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return True
#Automatic check and reset of the shoe of cards when it is empty   
def autocheckforsabot(PREVIOUS_SABOT,PREVIOUS_TRUECOUNT):
    if checkforsabot_empty(PREVIOUS_SABOT,PREVIOUS_TRUECOUNT):
        resetSabot(PREVIOUS_SABOT,PREVIOUS_TRUECOUNT)
 
#Draw        
def drawBoard(board,turn_player,bets_players,cashplayer,react=False):
    # Draw background of board.
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())
    
    # Draw grid lines of the board.
    """for x in range(BOARDWIDTH + 1):
        # Draw the horizontal lines.
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
         Draw the vertical lines.
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))"""

    # Draw the cards & in cases.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            
            #Get the coordinate to display the image
            centerx, centery = translateBoardToPixelCoord(x, y,True)
            contenu=board[x][y]
            if contenu in CARDS_TILE: 
                #Select the Image which corresponds to the card and display it on the board
                IMG=IM_CARDS[int(contenu)]
                
                IMG = pygame.transform.smoothscale(IMG, (SPACESIZE, SPACESIZE))
                board_IMGCARD=IMG.get_rect()
                board_IMGCARD.topleft = (centerx-SPACESIZE/2, centery-SPACESIZE/2)
                DISPLAYSURF.blit(IMG, board_IMGCARD)
                #pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
            if board[x][y] == HINT_TILE: #On ajoute l'aide
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))
                
    #Drawing bluebar that shows which player is playing
    drawbluebar(board,turn_player)
    
    #Drawing Count of the cards
    drawcount(board,turn_player,react)
    
    #Drawung the bets
    drawbets(board,bets_players)
    
    #Drawing the cashcount and reactions if it's the end of party
    drawcash(cashplayer)
    
    
    
     
#Drawing bluebar that shows which player is playing
def drawbluebar(boardgame,turn__player):
    BLUEBAR=pygame.image.load('ALL_FILES/BLUEBAR.jpg')
    BLUEBAR=pygame.transform.smoothscale(BLUEBAR,(60,10))
    board_Bluebar=BLUEBAR.get_rect()
    x1,y1=translateBoardToPixelCoord(2, BOARDWIDTH-1,True)
    x2,y2=translateBoardToPixelCoord(BOARDHEIGHT-1, 2,True)
    x3,y3=translateBoardToPixelCoord(2, 0,True)
    if turn__player!=4:
        if turn__player==1:
            barx,bary=x1-SPACESIZE/2,y1
        elif turn__player==2:
            barx,bary=x2-SPACESIZE*0.6,y2
        elif turn__player==3:
            barx,bary=x3-SPACESIZE*0.85,y3
        board_Bluebar.topleft=(barx,bary+SPACESIZE/2)
        DISPLAYSURF.blit(BLUEBAR, board_Bluebar)
    
    
        
#Drawung the bets     
def drawbets(boardgame,bets__players):
    Has_Splitted=[has_splitted(boardgame,i) for i in range(1,4)]
    x1,y1=translateBoardToPixelCoord(2, BOARDWIDTH-1,True)
    x2,y2=translateBoardToPixelCoord(BOARDHEIGHT-1, 2,True)
    x3,y3=translateBoardToPixelCoord(2, 0,True)
    pos=[[x1-15,y1+30],[x2-15,y2+30],[x3-15,y3+30]]
    IM_BET5_mini=pygame.transform.smoothscale(IM_BET5,(SPACESIZE,SPACESIZE))
    IM_BET10_mini=pygame.transform.smoothscale(IM_BET10,(SPACESIZE,SPACESIZE))
    IM_BET25_mini=pygame.transform.smoothscale(IM_BET25,(SPACESIZE,SPACESIZE))
    IM_BET50_mini=pygame.transform.smoothscale(IM_BET50,(SPACESIZE,SPACESIZE))
    IM_BET100_mini=pygame.transform.smoothscale(IM_BET100,(SPACESIZE,SPACESIZE))
    IM_BET200_mini=pygame.transform.smoothscale(IM_BET200,(SPACESIZE,SPACESIZE))
    for i in range(3):
        for j in range(2):
            if bets__players[i][j]!=0:
                
                if bets__players[i][j]==5:
                    bets_image=IM_BET5_mini
                elif bets__players[i][j]==10:
                    bets_image=IM_BET10_mini
                elif bets__players[i][j]==25:
                    bets_image=IM_BET25_mini
                elif bets__players[i][j]==50:
                    bets_image=IM_BET50_mini
                elif bets__players[i][j]==100:
                    bets_image=IM_BET100_mini
                elif bets__players[i][j]==200:
                    bets_image=IM_BET200_mini
                else:
                    bets_image=IM_BET25_mini
                
                if not Has_Splitted[i]:
                    bets_rect=bets_image.get_rect()
                    bets_rect.topleft = (pos[i][0], pos[i][1])
                    DISPLAYSURF.blit(bets_image, bets_rect)
                else:
                    bets_rect=bets_image.get_rect()
                    bets_rect.topleft = (pos[i][0]+2*SPACESIZE*(j-1/2),pos[i][1])
                    DISPLAYSURF.blit(bets_image, bets_rect)
                    
                   
#Return for each player each pile : WIN if the player win , LOOSE if the player Loose or Tie if the player Tie
def getResults(board,cashplayers,bets_players):
    
    
    convert_values=convertBoard(board)  #get the 11*11 matrix with the value of cards in it
    
     #Read the 11*11 matrix with values of cards and return:
     #The set of cards & the number of aces for each player
    card_allplayers , ace_allpos = get_cardplayers(convert_values)
    Results=[]
    
    #Calculate the maximal valid count of each player-dealer to deterine their results
    count=[]
    for i in range(1,5):
        count_player_i=[]
        for j in range(2):
            card_player_i_j=card_allplayers[2*(i-1)+j]
            ace_player_i_j=ace_allpos[i-1][j]
            countmin=sum(card_player_i_j)
            count_max_valid=countmin
            for w in range(ace_player_i_j+1):
                count_temp=countmin+10*w
                if count_temp<=21:
                    count_max_valid=count_temp
            count_player_i.append(count_max_valid)
        count.append(count_player_i)
    count_dealer=count[3][0]
    
    #Dealer has blacjack=1 if dealer has a blackjack
    dealer_has_blackjack=(count_dealer==21 and sum([w!=0 for w in card_allplayers[6]])==2)

    
    #Determine the results of each player with previous counts calculated 
    for i in range(3):
        Results_player_i=[]
        for j in range(2)  :
            
            count_i_j=count[i][j]
            player_i_j_has_blackjack=count_i_j==21 and sum([w!=0 for w in card_allplayers[2*i+j]])==2
            if bets_players[i][j]==0 : Results_player_i.append("NONE")
            elif count_i_j>21:
                Results_player_i.append("LOOSE")
                
            elif count_dealer>21:
                if  count_i_j==21 and sum([w!=0 for w in card_allplayers[2*i+j]])==2 :
                    
                    Results_player_i.append("BLACKJACK")
                    
                else:
                    Results_player_i.append("WIN")
                    
                
            elif count_dealer<count_i_j:
                if  player_i_j_has_blackjack :
                    Results_player_i.append("BLACKJACK")
                   
                else:
                    Results_player_i.append("WIN")
                    
            elif count_dealer>count[i][j]:
                Results_player_i.append("LOOSE")
            else:
                #if player_i_j_has_blackjack and dealer_has_blackjack:
                if dealer_has_blackjack:
                    Results_player_i.append("LOOSE")
                else:
                    #if dealer_has_blackjack:
                        #Results_player_i.append("LOOSE")
                    #else:
                    if player_i_j_has_blackjack:
                        Results_player_i.append("BLACKJACK")
                    else:
                        Results_player_i.append("TIE")
                            
                            
                        
        Results.append(Results_player_i)
    
    return Results
                
#Make win bets for each player knowing the results
def MakeWinBets(boardgame,cashplayer,bets_player,Matrix_DATA_2):
    Results=getResults(boardgame,cashplayer,bets_player)
    for i in range(3):
        SAUV=0
        for j in range(2):
            if Results[i][j]=="BLACKJACK":
                cashplayer[i]+=3*bets_player[i][j]
                SAUV+=2*bets_player[i][j]
                
            elif Results[i][j]=="WIN":
                cashplayer[i]+=2*bets_player[i][j]
                SAUV+=1*bets_player[i][j]
            elif Results[i][j]=="TIE":
                cashplayer[i]+=1*bets_player[i][j]
            else:
                SAUV-=bets_player[i][j]
        if i==1 or i==2 or i==0:
            Matrix_DATA_2[2].append(SAUV)
            
                
                
#Drawing the cashcount at any time and display reactions emotes if it's the end of party          
def drawcount(boardgame,turn__player,reaction=False):
    
    #Getting the set of cards and the number of aces for each player
    convert_values=convertBoard(boardgame)
    card_allplayers , ace_allpos = get_cardplayers(convert_values)
    
    #Calculate the counts for each player and return the two most useful to display
    count=[]
    for i in range(1,5):
        card_player_i=card_allplayers[2*(i-1)]
        ace_player_i=ace_allpos[i-1][0]
        countmin=sum(card_player_i)
        if i==4 and reaction==True:
            if countmin>21 :
                emote_cry_Surf=pygame.transform.smoothscale(emote_cry.convert_alpha(),(int(1.95*SPACESIZE),int(1.5*SPACESIZE)))
                emote_cry_Rect= emote_cry_Surf.get_rect()
                emote_cry_Rect.topright=(11*SPACESIZE,SPACESIZE)
                DISPLAYSURF.blit(emote_cry_Surf,emote_cry_Rect)
                playmusic1( "ALL_FILES/Sound2cry.ogg", 1) 
            for j in range(4):
                card_player_j=card_allplayers[2*j]
                countmin_j=sum(card_player_j)
                if True in [countmin_j+10*w==21 for w in range(ace_allpos[j][0] +1)]:
                    
                    x,y=getPosEmote(j)
                    
                    
                    emote_happy_Surf=pygame.transform.smoothscale(emote_happy.convert_alpha(),(int(1.32*SPACESIZE),int(1*SPACESIZE)))
                    emote_happy_Rect= emote_happy_Surf.get_rect()
                    emote_happy_Rect.topright=(x,y)
                    DISPLAYSURF.blit(emote_happy_Surf,emote_happy_Rect)
                    playmusic1( "ALL_FILES/Sound1cry.ogg", 1) 
                
        if ace_player_i>0:
            if ace_player_i==1:
                countmax=countmin+ace_player_i*10
                
            else:
                maxvalid=1
                countmax=countmin+10
                for i in range(1,ace_player_i+1):
                    count_temp=countmin+10*i
                    if countmin+10*i>21 and i>maxvalid:
                        maxvalid=i
                        countmax=count_temp
                    
        else:
            countmax=countmin
            
        countchar=str(countmin)+"/"+str(countmax)
        if countmax==21:
            if ace_player_i==1 and card_player_i[2]==0:
                count.append('BLACKJACK !')
            else:
                count.append(str(countmax))
        elif countmax==countmin:
            count.append(str(countmin))
        elif countmax>21:
            count.append(str(countmin))
        else: 
            count.append(countchar)
        
    #Drawing the circles and each count
    x1,y1=translateBoardToPixelCoord(2, BOARDWIDTH-1,True)
    x2,y2=translateBoardToPixelCoord(BOARDHEIGHT-1, 2,True)
    x3,y3=translateBoardToPixelCoord(2, 0,True)
    C1=pygame.draw.circle(DISPLAYSURF, BLACK, (int(x1-SPACESIZE), int(y1-SPACESIZE)), 20,1)
    C2=pygame.draw.circle(DISPLAYSURF, BLACK, (int(x2-SPACESIZE), int(y2-SPACESIZE)), 20,1)
    C3=pygame.draw.circle(DISPLAYSURF, BLACK, (int(x3-SPACESIZE), int(y3-SPACESIZE)), 20,1)
    C4=pygame.draw.circle(DISPLAYSURF, BLACK, (int(x2-SPACESIZE-15), int(YMARGIN+SPACESIZE+10)), 20,1)
    
    Count1 = FONT.render(count[0], True, TEXTCOLOR, TEXTBGCOLOR2)
    Count1Rect = Count1.get_rect()
    Count1Rect.topleft=(x1-SPACESIZE-10,y1-SPACESIZE-10)
    Count2 = FONT.render(count[1], True, TEXTCOLOR, TEXTBGCOLOR2)
    Count2Rect = Count1.get_rect()
    Count2Rect.topleft=(x2-SPACESIZE-10,y2-SPACESIZE-10)
    Count3 = FONT.render(count[2], True, TEXTCOLOR, TEXTBGCOLOR2)
    Count3Rect = Count1.get_rect()
    Count3Rect.topleft=(x3-SPACESIZE-10,y3-SPACESIZE-10)
    Count4 = FONT.render(count[3], True, TEXTCOLOR, TEXTBGCOLOR2)
    Count4Rect = Count4.get_rect()
    Count4Rect.topleft=(int(x2-SPACESIZE-25),int(YMARGIN+SPACESIZE))
    DISPLAYSURF.blit(Count1, Count1Rect)
    DISPLAYSURF.blit(Count2, Count2Rect)
    DISPLAYSURF.blit(Count3, Count3Rect)
    DISPLAYSURF.blit(Count4, Count4Rect)
    
#Draw the cash of each player below is cards
def drawcash(cash__player):
    cash_text=["CASH="+str(np.round(i,5))+"$" for i in cash__player]
    x1,y1=translateBoardToPixelCoord(2, BOARDWIDTH-1,True)
    x2,y2=translateBoardToPixelCoord(BOARDHEIGHT-1, 2,True)
    x3,y3=translateBoardToPixelCoord(2, 0,True)
  
    
    Count1 = FONT.render(cash_text[0], True, TEXTCOLOR, TEXTBGCOLOR3)
    Count1Rect = Count1.get_rect()
    Count1Rect.topleft=(x1-SPACESIZE,y1+2*SPACESIZE-10)
    
    Count2 = FONT.render(cash_text[1], True, TEXTCOLOR, TEXTBGCOLOR3)
    Count2Rect = Count1.get_rect()
    Count2Rect.topleft=(x2-SPACESIZE-2,y2+2*SPACESIZE-10)
    
    Count3 = FONT.render(cash_text[2], True, TEXTCOLOR, TEXTBGCOLOR3)
    Count3Rect = Count1.get_rect()
    Count3Rect.topleft=(x3-SPACESIZE-10,y3+2*SPACESIZE-10)
    
    a=int(np.round(pygame.time.get_ticks()/1000))
    divh,resth=int(a//3600),int(a%3600)
    restm,rests=int(resth//60),int(resth%60)
    timetext=str(divh)+"H "+str(restm)+"M "+str(rests)+"S"
    
    Counttime = FONT.render("Timer: "+str(timetext), True, BLACK, WHITE)
    CounttimeRect = Counttime.get_rect()
    CounttimeRect.topleft=(x1-SPACESIZE-35,y1-220)
    
    DISPLAYSURF.blit(Count1, Count1Rect)
    DISPLAYSURF.blit(Count2, Count2Rect)
    DISPLAYSURF.blit(Count3, Count3Rect)
    DISPLAYSURF.blit(Counttime, CounttimeRect)

#Return the position to display Emotes
def getPosEmote(i):
    if i==3:
        return (11*SPACESIZE,1*SPACESIZE)
    elif i==2:
        return (7*SPACESIZE,6*SPACESIZE)
    elif i==1:
        return (11*SPACESIZE,7*SPACESIZE)
    elif i==0:
        return (14*SPACESIZE,6*SPACESIZE)
        
# Read the coordinate where the click is located and return the moove decision if the player
# clicked on a moove button
def get_decision(mousex, mousey):
    

    if mousex > BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN and mousex < BOARDWIDTH*SPACESIZE+ 1.1*XMARGIN+2*SPACESIZE:
         if mousey > 5*YMARGIN and mousey < 5*YMARGIN+SPACESIZE:
             return 'DEAL'
         elif mousey >8*YMARGIN and mousey < 8*YMARGIN+SPACESIZE:
             return 'HIT'
         elif mousey > 11*YMARGIN and mousey < 11*YMARGIN+SPACESIZE:
             return 'STAND'
         elif mousey > 14*YMARGIN and mousey < 14*YMARGIN+SPACESIZE:
             return 'DOUBLE'
         elif mousey > 17*YMARGIN and mousey < 17*YMARGIN+SPACESIZE:
             return 'SPLIT'
    return None
    
## Read the coordinate where the click is located and return the bet decision if the player
# clicked on a bet button
def  get_betchoice(mousex,mousey):
    if mousex> 0.1*XMARGIN and mousex<0.1*XMARGIN+2*SPACESIZE:
        if mousey > 4*YMARGIN and mousey < 4*YMARGIN+2*SPACESIZE:
             return ('bet5',5)
        elif mousey > 8*YMARGIN and mousey < 8*YMARGIN+2*SPACESIZE:
             return ('bet25',25)
        elif mousey > 12*YMARGIN and mousey < 12*YMARGIN+2*SPACESIZE:
             return ('bet50',50)
        elif mousey > 16*YMARGIN and mousey < 16*YMARGIN+2*SPACESIZE:
             return ('bet100',100)
      
         
    return (None,0)


"""def drawInfo(board, playerTile, computerTile, turn):
    # Draws scores and whose turn it is at the bottom of the screen.
    scores = getScoreOfBoard(board)
    scoreSurf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[playerTile]), str(scores[computerTile]), turn.title()), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
    DISPLAYSURF.blit(scoreSurf, scoreRect)"""

#Reset the board between each game and give a card to the dealer before the beginning
def resetBoard(board,sabot_actual,truecount_actual):
    # Blanks out the board it is passed, and sets up starting tiles.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE
            
    board[0][2]=sabot_actual[0]
    card=sabot_actual[0]
    del sabot_actual[0]
    autocheckforsabot(sabot_actual,truecount_actual)
    truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
    truecount_actual[1]+=1
    truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
    
    
# Creates a brand new, empty board data structure.   
def getNewBoard():
    
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    
    return board

# Return  the set of cards of the dealer
def get_card_dealer(board) :
    VALUES_1O=[str(i) for i in range(1,5)] 
    VALUE_ACE='0'
    VALUEOTHER=[str(i) for i in range(5,13)]
    contenu=board[0][2]
    
    if contenu==VALUE_ACE:
        return 'A'
    if contenu in VALUES_1O:
        return '10'
    if  contenu in VALUEOTHER:
        return str(14-int(contenu))

#Get the basic strategy "states" that can be saved as DATA
def get_last_count(boardgame,turn_players,bets_players,standMoove):
    VALUES_1O=[str(i) for i in range(1,5)] 
    VALUES_DOUBLE=[9,10,11]
    i1,j1=convertPosList_to_Board(0,turn_players)
    i2,j2=convertPosList_to_Board(1,turn_players)
    i3,j3=convertPosList_to_Board(2,turn_players)
    
    first_card=boardgame[i1][j1]
    second_card=boardgame[i2][j2]
    third_card=boardgame[i3][j3]
        
    #VERIFY IS PLAYER COULD SPLIT OR HAS SPLIT
    if first_card==second_card or bets_players[turn_players-1][1]!=0:  
        return None
    
    #VERIFY IS PLAYER HAS AN ACE AND ALLOW IT TO BE A DATA ONLY IF THERE IS TWO CARDS MAXIMUM
    if '0' in [boardgame[convertPosList_to_Board(i,turn_players)[0]][convertPosList_to_Board(i,turn_players)[1]] for i in range(6) ]:
        
        if third_card==EMPTY_SPACE:
                
            if first_card=='0':
                if second_card in VALUES_1O:
                    return 'A-10'
                
                return 'A-'+str(14-max(4,int(second_card)))
            
            if first_card in VALUES_1O:
                return 'A-10'
            
            return 'A-'+str(14-int(first_card))
         
            
        else:
            
            convert__values=convertBoard(boardgame)
            card_allplayers , ace_allpos = get_cardplayers(convert__values)
            card_player=card_allplayers[2*(turn_players-1)]
            ace_player=ace_allpos[turn_players-1][0]
            imax=max([w  for w in range(len(card_player)) if card_player[w]!=0 ])
            
            
            sum1=sum(card_player[0:imax])
            if first_card=='0':
                
                
                if 1 in card_player[2:imax]:
                    return None
                if sum1 in VALUES_DOUBLE:
                    if imax==2:
                        
                        
                        return 'A-'+str(14-max(4,int(second_card)))
                        
                    else:
                        return sum1
                return None
            elif second_card=='0':
                if 1 in card_player[2:imax]:
                    return None
                if sum1 in VALUES_DOUBLE:
                    if imax==2:
                        
                        
                        
                        return 'A-'+str(14-max(4,int(second_card)))
                    
                    else: 
                        return sum1
                return None
            return None
                
                    
                
            
    #ELSE RETURN THE COUNT OF THE CARDS
    else: 
        return None
        convert__values=convertBoard(boardgame)
        card_allplayers , ace_allpos = get_cardplayers(convert__values)
        card_player=card_allplayers[2*(turn_players-1)]
        if third_card==EMPTY_SPACE:
            imax=2
        else:
            
            imax=max([w  for w in range(len(card_player)) if card_player[w]!=0 ])
            if standMoove==True:
                imax+=1
        
        return sum(card_player[0:imax])

        
#Take the board (11*11 matrix containing text) , return a 11*11 matrix containing the value of cards
def convertBoard(board):
    
    TRUE_VALUE = []
    for i in range(BOARDWIDTH):
        TRUE_VALUE.append([0] * BOARDHEIGHT)
    
    #King, Queen, Valet and Ten  
    VALUES_1O=[str(i) for i in range(1,5)] 
    
    #Conversion Loop
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            contenu=board[x][y]
            if contenu==EMPTY_SPACE:
                TRUE_VALUE[x][y]=0
                
            #DETECT THE ACE which can take two values 1 and 11, and signal it
            elif contenu=='0':
                TRUE_VALUE[x][y]=1
                #SEPARATE DEALER PLAYER 1 FROM PLAYER 2 PLAYER 3
       
                            
                        
            elif contenu in VALUES_1O: #ON ISOLE CE GROUPE CAR DIFFICILE DE TROUVER 
                                        #UNE FORMULE DE CONVERSION SIMPLE 
                TRUE_VALUE[x][y]=10
            else:
                if contenu!='0':
                    TRUE_VALUE[x][y]=14-int(contenu)
                
    return TRUE_VALUE

                
#Take the converted Board (11*11 matrix containing values of cards of each player)  
#Returns a 8*7 Matrix which the true value of cards and delete "EMPTY_SPACE" 
#The dimension is 8*7 because each of the 3 player & dealer can hit 7 cards max, then 2*7 if they split
#Example: the first two lines represents the value of the cards of Player1 for pile1 and pile2          
def get_cardplayers(convert_values):
    
    MATRIX=[]
    HAS_ACE=[[0,0],[0,0],[0,0],[0,0]] #contain for each player' pile the number of aces in it
    
    #Players 1 (right of board), 2 (bottom of board), 3 (on left)
    CARDS_P1=[[convert_values[i][BOARDWIDTH-1] for i in range(2,BOARDHEIGHT-2)],[convert_values[i][BOARDWIDTH-2] for i in range(2,BOARDHEIGHT-2)]]
    CARDS_P2=[[convert_values[BOARDHEIGHT-1][i] for i in range(2,BOARDWIDTH-2)], [convert_values[BOARDHEIGHT-2][i] for i in range(2,BOARDWIDTH-2)]]
    CARDS_P3=[[convert_values[i][0] for i in range(2,BOARDHEIGHT-2)],[convert_values[i][1] for i in range(2,BOARDHEIGHT-2)]]
    
    #Dealer: upward the board
    CARDS_DEALER=[[convert_values[0][i] for i in range(2,BOARDWIDTH-2)],[convert_values[1][i] for i in range(2,BOARDWIDTH-2)]]
    #Fill the matrix
    TEMP_MATRIX=[CARDS_P1,CARDS_P2,CARDS_P3,CARDS_DEALER]
    for i in range(len(TEMP_MATRIX)):
        for j in range(2):
            row=TEMP_MATRIX[i][j]
            MATRIX.append(row)
            if 1 in row:
                HAS_ACE[i][j]+=1
    
    return MATRIX,HAS_ACE

# Return if one's can bet by reading the board
def isValid_to_bet(board):
   for i in range(BOARDHEIGHT):
       for j in range(BOARDWIDTH):
           if board[i][j]!=EMPTY_SPACE and i!=0 and j!=2:
               return False
   return True

        
# Return if the Move can be executed after reading the board
def isValidMove(board, turn_player,turn_pile,decision,bets_player):
    # Returns False if the player's move is invalid. If it is a valid
    
    #Charge the matrix of cards and aces position (player,pile)
    convert_values=convertBoard(board)

    card_allplayers , ace_allpos = get_cardplayers(convert_values)
    
    
    #Take only the values of cards and aces position for the player considered
    card_player=[card_allplayers[2*(turn_player-1)],card_allplayers[2*turn_player-1]]
    ace_player=ace_allpos[turn_player-1]
    
    #Take the pile considered for this player
    card_player_pile=card_player[turn_pile-1]
    ace_player_pile=ace_player[turn_pile-1]
    
    #Take the sum of this pile of cards
    count_pile=sum(card_player_pile)
    
    
    #VALID MOVE FOR THE DEALER
    if turn_player==4:
        
        
        
        if decision=='HIT':
            if card_player_pile[6]==0:
                
                if 1 not in card_player_pile:
                    if count_pile<17 :
                        return True
                else:
                    if count_pile+10==21:
                        return False
                    if count_pile<17 :
                        return True
                    return False
                    
                return False
                
            return False
        
        if decision=='STAND': #count_pile est le min ok
            if True in [count_pile+10*i>=17 for i in range(ace_player_pile+1)]:
                return True
            return False
        return False
                
    #VALID MOVE FOR THE PLAYER
    else:
       
    #"Bust" or "Blackjack" => Validmove is an empty set
        #if decision=='DEAL'
        
        if count_pile>21:
            return False
        
        #The player can hit cards if he has no bust, no blackjack and less than 7 cards
        if decision=='HIT':
            if card_player_pile[6]==0 and card_player_pile[0]!=0:
                if count_pile<21 and not True in [count_pile+10*i==21 for i in range(ace_player_pile+1)] :
                    return True
                return False
                    
            return False
        
        #If he has no bust and no blackjack he can always stand
        elif decision=='STAND':
            if card_player_pile[0]!=0:
                return True
            return False
        
        #The player can split if:
        #He has not splitted yet (0 cards in pile 2), 
        #The two cards of pile 1 are the same,
        #The player is playing pile 1 and he has exactly two cards distributed 
        elif decision=='SPLIT':
             
            #WE CHECK IF THE TWO CARDS ARE THE SAME AND IF THE PLAYER NEVER SPLIT AND 
            #IF WE ARE PLAYING THE FIRST PILE AND IF THERE IS ONLY TWO CARDS DISTRIBUTED
            #NON SIMPLIFIABLE ATTENTION!
            if card_player_pile[0]!=0:
                posx,posy=convertPosList_to_Board(0,turn_player)
                posxNEXT,posyNEXT=convertPosList_to_Board(1,turn_player)
                if board[posx][posy]==board[posxNEXT][posyNEXT] and card_player[1][0]==0 and turn_pile==1 and card_player_pile[2]==0:
                    return True
                return False
            return False
                
        #The player can double :
        #If the sum of his cards are 9,10,11 and he can hit a new card
        #IF he received two cards exactly in his pile
        elif decision=='DOUBLE':
            RANGE_CORRECT=[9,10,11]
            #CHECK IF HE CAN HIT 
            if card_player_pile[6]==0:
            #CHECK IF HE HAS A COMBINAISON OF CARD IN THE RANGE
                
                if True in [count_pile+10*i in RANGE_CORRECT for i in range(ace_player_pile+1)]:
                    #CHECK IF HE HAS exactly two cards in his pile and that this is pile 1 
                    if card_player_pile[0]!=0  :
                    
                        return True
            
            return False
        elif decision=='DEAL':
            
            betslist=[]
            for i in range(3):
                for j in range(2):
                    betslist.append(bets_player[i][j])
            
            if isValid_to_bet(board):  
                if betslist[2*(turn_player -1) ]==0 :
                    return True
            return False
        
    return False

#Return all Valid Moves for one player
def getValidMoves(board, turn_player,turn_pile,bets_player):
    
    # Returns a list of (x,y) tuples of all valid moves.
    validMoves = []
    
    for w in OPTIONS:
        
        if isValidMove(board, turn_player,turn_pile,w,bets_player) != False:
            validMoves.append(w)
    return validMoves
        
            
# Returns True if the coordinates are located on the board.
def isOnBoard(x, y):

    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


#def getBoardWithValidMoves(board, tile):
    # Returns a new board with hint markings.
    #dupeBoard = copy.deepcopy(board)

    #for x, y in getValidMoves(dupeBoard, tile):
        #dupeBoard[x][y] = HINT_TILE
    #return dupeBoar




def enterMode():
    # Draws the text and handles the mouse click events for letting
    # the player choose which Mode he wants to play.  Returns
    # 'MODE_ML' if the player chooses to see ML results
    # 'MODE_NORMAL" if the player chooses to play

    # Create the text.
    textSurf = FONT.render('Do you want to play like an ENSAE student?', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    xSurf = BIGFONT.render('Normal Player', True, TEXTCOLOR, TEXTBGCOLOR1)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 160, int(WINDOWHEIGHT / 2) + 40)

    oSurf = BIGFONT.render('Machine Learning', True, TEXTCOLOR, TEXTBGCOLOR1)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 120, int(WINDOWHEIGHT / 2) + 40)

    while True:
        # Keep looping until the player has clicked on a color.
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return MODE_PLAY
                elif oRect.collidepoint( (mousex, mousey) ):
                    return MODE_ML

        # Draw the screen.
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        #MAINCLOCK.tick(FPS)

## Place the cards on the board, update cash and bets, check if sabot empty, play bets sound effects
def makeMove(board,decision,turn_players,sabot_actual,turn_pile,bets_players,bets_actual,cashplayer,truecount_actual):
    
    
    if turn_players<4:
        if decision=='DEAL':
            
            bets_players[turn_players-1][turn_pile-1]+=bets_actual
            
            cashplayer[turn_players-1]-=bets_actual
            
            if turn_players==3:
                
                board[BOARDHEIGHT-1][2]=sabot_actual[0]
                
                card=sabot_actual[0]
                
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                
                board[BOARDHEIGHT-1][3]=sabot_actual[0]
                card=sabot_actual[0]
                
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                
                board[2][BOARDWIDTH-1]=sabot_actual[0]
                card=sabot_actual[0]
                
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                
                board[3][BOARDWIDTH-1]=sabot_actual[0]
                card=sabot_actual[0]
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                
                board[2][0]=sabot_actual[0]
                card=sabot_actual[0]
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                
                board[3][0]=sabot_actual[0]
                card=sabot_actual[0]
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                
            
                
            
                
            
                
                
        
        elif decision=='HIT' or decision=='DOUBLE':#PAS OUBLIER BETS DANS MAIN LOOP
            xNext,yNext=searchfornextPos(board,turn_players,turn_pile)
            board[xNext][yNext]=sabot_actual[0]
            card=sabot_actual[0]
            del sabot_actual[0]
            autocheckforsabot(sabot_actual,truecount_actual)
            truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
            truecount_actual[1]+=1
            truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
            if decision=='DOUBLE':
                bets_players[turn_players-1][turn_pile-1]*=2
                cashplayer[turn_players-1]-=bets_players[turn_players-1][turn_pile-1]/2
                #playmusic1( "sound_bet.ogg", 1) 
            
            
                
                        
                
            
            
        elif decision=='SPLIT':   
            xNext,yNext=searchfornextPos(board,turn_players,2)
            xPrev,yPrev=searchforprevPos(board,turn_players,1)
            switch_card=board[xPrev][yPrev]
            board[xPrev][yPrev]=EMPTY_SPACE
            board[xNext][yNext]=switch_card
            bets_players[turn_players-1][0]=bets_actual
            bets_players[turn_players-1][1]=bets_actual
            
            #playmusic1( "sound_bet.ogg", 1) 
            cashplayer[turn_players-1]-=bets_actual

          
            
            
            
    elif turn_players==4:
        if decision=='HIT':
            xNext,yNext=searchfornextPos(board,turn_players,turn_pile)
            if xNext!=None:
                
                board[xNext][yNext]=sabot_actual[0]
                card=sabot_actual[0]
                del sabot_actual[0]
                autocheckforsabot(sabot_actual,truecount_actual)
                truecount_actual[0]+= - (int(card)<=4 ) + (int(card)>=8 )
                truecount_actual[1]+=1
                truecount_actual[2]=int(truecount_actual[0]/((int(((313-truecount_actual[1])/0.52)))/100))
                convert_values=convertBoard(board)
                card_allplayers , ace_allpos = get_cardplayers(convert_values)
                card_player=[card_allplayers[2*(turn_players-1)],card_allplayers[2*turn_players-1]]
                ace_player=ace_allpos[turn_players-1]
                card_player_pile=card_player[turn_pile-1]
                ace_player_pile=ace_player[turn_pile-1]
                #Take the sum of this pile of cards
                count_pile=sum(card_player_pile)
    
            
                
    pygame.display.update()
    
    checkForQuit()
        
#Search the next coordinates in the board to add the next card for one player
def searchfornextPos(board,turn_player,pile):
    actual_convert=convertBoard(board)
    actual_Cards, actual_Aces=get_cardplayers(actual_convert)
    for i in range(7):
        
        if actual_Cards[2*(turn_player-1) + pile-1][i]==0:
            if turn_player==1:
                return (2+i,BOARDWIDTH-pile)
            elif turn_player==2:
                return (BOARDHEIGHT-pile,2+i)
            elif turn_player==3:
                return (2+i,pile-1)
            else:
                return (pile-1,2+i)
    return None,None

#Search the previous card's coordinates in the board for one player
def searchforprevPos(board,turn_player,pile):
    actual_convert=convertBoard(board)
    actual_Cards, actual_Aces=get_cardplayers(actual_convert)
    for i in range(7):
        
        if actual_Cards[2*(turn_player-1) + pile-1][i]==0:
            if turn_player==1:
                return (1+i,BOARDWIDTH-pile)
            elif turn_player==2:
                return (BOARDHEIGHT-pile,1+i)
            elif turn_player==3:
                return (1+i,pile-1)
            else:
                return (pile-1,1+i)
    return None
            
                
def isOnCorner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or \
           (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or \
           (x == BOARDWIDTH and y == BOARDHEIGHT)

# Apply the strategy of the dealer
def getComputerMove(board,turn_players,turn_pile,bets_player):
    # Given a board and the computer's tile, determine where to
    # move and return that move as a [x, y] list.
    possibleMoves = getValidMoves(board, turn_players,turn_pile,bets_player)
    return possibleMoves

# Check at any time if "QUIT" is selected or ESCAPE pressed and quit pygame if it's the case
def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()
    
    
    # si ce code est exécuté en tant que script principal 
    #(appelé directement avec Python et pas importé), alors exécuter cette fonction.