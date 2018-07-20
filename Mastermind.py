# Mastermind
# Author: Nico Mueller
# 2018

import numpy
import serial
import time

TWO_PLAYER = False  #Turns on that a player set the riddle
NOINPUT_WAIT = 0  #delay after no input   #min 3 colors, element 0 = empty, last element = hide/blink cursor

ser = serial.Serial('/dev/ttyACM0') #TODO https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino

#initiate matrix, winningRow

class LEDMatrix():
    import unicornhat as unicorn
    def __init__(self):
        self.matrix = numpy.zeros([7,4])
        self.winningRow = numpy.random.randint(1,4,size=(4))  #randomly generates the winningrow
        self.matrix= numpy.vstack([self.matrix, self.winningRow])   #adds winning row to LEDMatrix
        self.tempNewRow = numpy.zeros(4) #used to check if pin was correct and therefore cannot be changed anylonger in the next row
        self.cursorX = 0
        self.cursorY = 0 # selected LED
        self.COLORS = [(0,0,0),(255,255,0), (255,0,0),(0,255,0), (0,0,255),(255,255,255)]
        self.unicorn.set_layout(self.unicorn.PHAT)
        self.unicorn.brightness(0.2)
        self.BLINK_WAIT= 0.3    #time between blinks of leds

    def getPinValue(self,x,y):
        return self.matrix[y][x]
    def setPinValue(self,x,y,value):
        self.matrix[y][x] = value

    def getWinningRow(self):
        return self.winningRow
    
    def getTempNewRow(self):
        return self.tempNewRow
    
    def getCursorX(self):
        return self.cursorX
    
    def setCursorX(self,value):
        self.cursorX = value
    
    def getCursorY(self):
        return self.cursorY
    
    def setCursorY(self,value):
        self.cursorY = value
    
    def getMaxRow(self):
        return self.matrix.shape[0]-1
    
    def getMaxColumn(self):
        return self.matrix.shape[1]
    
    def setPin(self,x,y,value):
        self.matrix[y][x] = value
    #Player colors, 2 colors are reserved for blank and empty field blinking cursor (white)
    def getMaxColor(self):
        return len(self.COLORS)-2

    def hideLastRow(self):
        for x in range(0,self.getMaxColumn()):
            self.unicorn.set_pixel(self.getMaxRow(),x,self.COLORS[-1])
            
    def blinkCursor(self):
        tmpColor = self.matrix[self.cursorY][self.cursorX]
        if tmpColor == 0:
            self.unicorn.set_pixel(self.cursorY,self.cursorX,self.COLORS[-1]) #last color = white
            self.unicorn.show()
            time.sleep(self.BLINK_WAIT)
            self.unicorn.set_pixel(self.cursorY,self.cursorX,self.COLORS[0]) #no color
            self.unicorn.show()
        else:
            time.sleep(self.BLINK_WAIT)
            self.unicorn.set_pixel(self.cursorY,self.cursorX,self.COLORS[0]) #no color
            self.unicorn.show()
            time.sleep(self.BLINK_WAIT)
            self.unicorn.set_pixel(self.cursorY,self.cursorX,self.COLORS[int(tmpColor)]) 
            self.unicorn.show()

    #Outputs the matrix to the phat
    #bool init to set if the winning row should be shown in case of a 2 player game riddle setting process
    #TODO move to game object
    def outputMatrix(self,init,hasWon,hasLost):
        for x in range(0, self.matrix.shape[0]):
            for y in range(0, self.matrix.shape[1]):
                self.unicorn.set_pixel(x,y,self.COLORS[int(self.matrix[x][y])])
        if init == False and hasWon == False and hasLost == False:
            self.hideLastRow()
        self.unicorn.show()
    #gets first free pin to set cursor to
    def getFirstFreePin(self):
        res = 0
        for i in range(3,-1,-1):
            if self.matrix[self.cursorY][i] == 0:
                res = i
        return res
    
    def animateWin(self):
        self.unicorn.clear()
        self.unicorn.show()
        for y in range(0,8):
          self.unicorn.set_pixel(y,0,255,0,0)
          self.unicorn.show()
          time.sleep(0.05)
    
        for y in range(0,8):
          self.unicorn.set_pixel(y,1,0,255,0)
          self.unicorn.show()
          time.sleep(0.05)
    
        for y in range(0,8):
          self.unicorn.set_pixel(y,2,0,0,255)
          self.unicorn.show()
          time.sleep(0.05)
    
        for y in range(0,8):
          self.unicorn.set_pixel(y,3,255,0,255)
          self.unicorn.show()
          time.sleep(0.05)
    
    # sad smiley
    def animateLoss(self):
        self.unicorn.clear()
        self.unicorn.show()
        self.unicorn.set_pixel(5,1,255,255,255)
        self.unicorn.set_pixel(5,2,255,255,255)
        self.unicorn.set_pixel(3,1,255,255,255)
        self.unicorn.set_pixel(3,2,255,255,255)
        self.unicorn.set_pixel(2,0,255,255,255)
        self.unicorn.set_pixel(2,3,255,255,255)
        self.unicorn.show()
        time.sleep(3)
    
    def checkBoard(self):
        won = True  #can be removed?
        correctPins = 0
        for x in range(0,self.getMaxColumn()):
            if self.winningRow[x] != self.matrix[self.cursorY][x]:
                won = False
            else:
                correctPins = correctPins+1
                if self.cursorY < self.getMaxRow() -1:
                    self.matrix[self.cursorY+1][x] = self.matrix[self.cursorY][x]
                    self.tempNewRow[x] = self.matrix[self.cursorY][x]
   #saveNextRow
        if won:
            if self.cursorY < self.getMaxRow() -1:
                #reset next row to empty
                for x in range(0,self.getMaxColumn()):
                    self.matrix[self.cursorY+1][x] = 0
            self.animateWin()
        return won
            
class Game():
    def __init__(self,TwoPlayer):
        self.ledMatrix = LEDMatrix()
        self.hasLost = False
        self.hasWon = False
        if TwoPlayer: self.start2Playergame()
    def getGameMatrix(self):
        return self.ledMatrix
    def start2PlayerGame(self):
        #Two playergame, 1st player sets riddle
        self.ledMatrix.setCursorX(0)
        self.ledMatrix.setCursorY(self.ledMatrix.getMaxRow())
        for f in range(0,self.ledMatrix.getMaxColumn()):
            self.ledMatrix.setPin(self.ledMatrix(self.ledMatrix.getMaxRow(),f,1))
        for i in range(0,self.self.ledMatrix.getMaxColumn()):
          confirmed = False
          self.ledMatrix.setCursorX(i)
          while confirmed is not True:
              self.ledMatrix.outputMatrix(True,self.hasWon,self.hasLost)
              self.ledMatrix.blinkCursor()
              x = ser.readline()
              x = x.decode('utf8')
              x = x[:-2]
              if x=="Down":
                  if self.ledMatrix.getValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX()) > 1:
                     self.ledMatrix.setValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX(),self.ledMatrix.getValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX()) -1)
              elif x=="Up":
                  if self.ledMatrix.getValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX()) < self.ledMatrix.getMaxColor():
                     self.ledMatrix.setValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX(),self.ledMatrix.getValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX()) +1)
              elif x=="Confirm" and self.ledMatrix.getValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX()) > 0:
                  confirmed = True
                  self.ledMatrix.getWinningRow()[i] = self.ledMatrix.getValue(self.ledMatrix.getCursorY(),self.ledMatrix.getCursorX())
              ser.flushInput()
        self.ledMatrix.setCursorX(0)
        self.ledMatrix.setCursorY(0)
    
    def getHasLost(self):
        return self.hasLost
    
    def setHasLost(self,value):
        self.hasLost = value
        
    def getHasWon(self):
        return self.hasWon
    
    def setHasWon(self,value):
        self.hasWon = value
    def check(self):
        if self.ledMatrix.checkBoard():
            self.setHasWon(True)

    def joystickUp(self):
        pin = self.ledMatrix.getPinValue(self.ledMatrix.getCursorX(),self.ledMatrix.getCursorY())
        if pin < self.ledMatrix.getMaxColor():
            pin=pin+1
            self.ledMatrix.setPinValue(self.ledMatrix.getCursorX(),self.ledMatrix.getCursorY(),pin)
    
    def joystickDown(self):
        pin = self.ledMatrix.getPinValue(self.ledMatrix.getCursorX(),self.ledMatrix.getCursorY())
        if pin > 1:
            pin=pin-1
            self.ledMatrix.setPinValue(self.ledMatrix.getCursorX(),self.ledMatrix.getCursorY(),pin)
    
    def joystickLeft(self):
        for x in range(self.ledMatrix.getCursorX()-1,-1,-1):
            if self.ledMatrix.getTempNewRow()[x] == 0:
                self.ledMatrix.setCursorX(x)
                break
    
    def joystickRight(self):
        for x in range(self.ledMatrix.getCursorX()+1,self.ledMatrix.getMaxColumn()):
            if self.ledMatrix.getTempNewRow()[x] == 0:
                self.ledMatrix.setCursorX(x)
                break

    def requiresInput(self):
        res = -1
        for i in range(3,-1,-1):
            if self.ledMatrix.getPinValue(i,self.ledMatrix.getCursorY()) == 0:
                res = i
        return res
    
    def confirm(self):
        # Dont allow confirmation until all is set
        riPin = self.requiresInput()
        if riPin == -1:
            if self.ledMatrix.getCursorY() < self.ledMatrix.getMaxRow()-1:
                self.check()
            else:
                self.setHasLost(True)
                self.ledMatrix.animateLoss()
            if self.hasWon is not True and self.hasLost is not True:
                self.ledMatrix.setCursorY(self.ledMatrix.getCursorY()+1)
                self.ledMatrix.setCursorX(self.ledMatrix.getFirstFreePin())
        else:
            self.ledMatrix.setCursorX(riPin)


game = Game(TWO_PLAYER)

# Main loop
while 1:
    game.getGameMatrix().outputMatrix(False,game.getHasWon(),game.getHasLost())
    if game.getHasWon() is not True and game.getHasLost() is not True and game.getGameMatrix().getCursorY() < game.getGameMatrix().getMaxRow():
      game.getGameMatrix().blinkCursor()
    x = ser.readline()
    x = x.decode('utf8')
    x = x[:-2]
    if game.getHasWon() is not True and game.getHasLost() is not True and game.getGameMatrix().getCursorY() < game.getGameMatrix().getMaxRow():
        if x=="Confirm": game.confirm()   
        elif x=="Down": game.joystickDown()
        elif x=="Up": game.joystickUp()
        elif x=="Left": game.joystickLeft()
        elif x=="Right": game.joystickRight()  
    elif x=="Confirm": game = Game(TWO_PLAYER)
    ser.flushInput()
    