#TODO:
#RAFIFUF SHOULD COMMENT CODE
#Icons
#Compile
#------------

import sys, random, threading
from playsound import playsound
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QMessageBox, QToolBar, QLabel, QComboBox, QSizePolicy
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #Scales to other devices

class MainWindow(QMainWindow):
    def __init__(self):
        #Setting default values
        self.InitialDelay = 1000
        self.FlashOnDelay = 150
        self.FlashOffDelay = 650
        self.GameOverFlashDelay = 200
        self.SoundDelay = 20
        self.UserExtraMoveNeeded = False
        self.GameMode = "Classic"
        self.Round = 0
        self.PlayerTurnIndicator = None
        
        #Super Init inherits everything, everything afterwards gets overrided (for ben)
        super().__init__()
        self.setWindowTitle("Shimon Says")
        self.setStyleSheet(f"background-color: black;")
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        
        self.toolbar = QToolBar("MainBar")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.toggleViewAction().setEnabled(False)

        GameModeLabel = QLabel("Game Mode")
        GameModeLabel.setFont(QFont("Arial", 10))
        GameModeLabel.setStyleSheet("color: white;")
        GameModeLabel.setContentsMargins(10, 5, 10, 5) #left, up, right, down
        self.toolbar.addWidget(GameModeLabel)
        
        self.GameModeCombo = QComboBox()
        self.GameModeCombo.addItems(["Classic", "Multiplayer", "Blind"])
        self.GameModeCombo.setStyleSheet("font-size: 10pt; selection-background-color: black; border-color: grey; color: white; border: 2px solid #616A6B; padding-right: 5px;")
        self.GameModeCombo.currentTextChanged.connect(self.GameModeChanged)
        self.toolbar.addWidget(self.GameModeCombo)
        
        Spacer1 = QWidget()
        Spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(Spacer1)

        '''
        self.PlayerTurnIndicatorLabel = QLabel(f"Turn: {self.PlayerTurnIndicator}")
        self.PlayerTurnIndicatorLabel.setFont(QFont("Arial", 10))
        self.PlayerTurnIndicatorLabel.setStyleSheet("color: white;")
        self.PlayerTurnIndicatorLabel.setContentsMargins(15, 5, 15, 5) #left, up, right, down
        #self.PlayerTurnIndicatorLabel.setHidden(True)
        self.PlayerTurnIndicatorLabel.hide()
        self.toolbar.addWidget(self.PlayerTurnIndicatorLabel)
        '''
        
        Spacer2 = QWidget()
        Spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(Spacer2)
        
        self.RoundLabel = QLabel(f"Round: {self.Round}")
        self.RoundLabel.setFont(QFont("Arial", 10))
        self.RoundLabel.setStyleSheet("color: white;")
        self.RoundLabel.setContentsMargins(30, 5, 10, 5) #left, up, right, down
        self.toolbar.addWidget(self.RoundLabel)

        MainLayout = QVBoxLayout()
        GameLayout = QGridLayout()
        MainLayout.addLayout(GameLayout)
        
        self.GreenButton = ColouredButton("green", "#57D658","Green.wav")
        GameLayout.addWidget(self.GreenButton, 0, 0)
        
        self.RedButton = ColouredButton("#CC0000", "#FF0000", "Red.wav")
        GameLayout.addWidget(self.RedButton, 0, 1)

        self.YellowButton = ColouredButton("#CCCC00", "#FFFF00", "Yellow.wav") #default, flash
        GameLayout.addWidget(self.YellowButton, 1, 0)
        
        self.BlueButton = ColouredButton("#0000B2", "#0000FF", "Blue.wav")
        GameLayout.addWidget(self.BlueButton, 1, 1)
        
        self.SetButtonState(False)
        
        self.StartButton = QPushButton("Start")
        self.StartButton.clicked.connect(lambda: self.StartGame())
        self.StartButton.setStyleSheet("background-color: white;")
        MainLayout.addWidget(self.StartButton)
        
        #dummy widget pyqt5 needs it
        widget = QWidget()
        widget.setLayout(MainLayout)
        self.setCentralWidget(widget)
    
    def GameModeChanged(self, Text):
        self.GameMode = Text
        
        '''
        #self.PlayerTurnIndicatorLabel.setHidden(False if self.GameMode == "Multiplayer" else True)
        self.PlayerTurnIndicatorLabel.show()
        '''

    def SetButtonState(self, State):
        #Enable/Disable User input of buttons when computer round is running
        self.GreenButton.setEnabled(State)
        self.RedButton.setEnabled(State)
        self.YellowButton.setEnabled(State)
        self.BlueButton.setEnabled(State)
    
    def ResetButtonFlash(self):
        #Sets buttons back to their default colour when starting a new game
        self.GreenButton.setStyleSheet(f"background-color: {self.GreenButton.Colour};")
        self.RedButton.setStyleSheet(f"background-color: {self.RedButton.Colour};")
        self.YellowButton.setStyleSheet(f"background-color: {self.YellowButton.Colour};")
        self.BlueButton.setStyleSheet(f"background-color: {self.BlueButton.Colour};")
        
    def StartGame(self):
        self.StartButton.setEnabled(False)
        self.toolbar.setEnabled(False)
        self.StartButton.setStyleSheet("background-color: #C2C2C2;")
        self.ResetButtonFlash()
        self.NeededMoves = []
        self.PlayerMoves = []
        self.Round = 1
        self.RoundLabel.setText(f"Round: {self.Round}")
                                
        #If gamemode were blind, it would set up the initial sequence
        if self.GameMode == "Blind":
            self.BlindModeSequence = [self.GreenButton, self.RedButton, self.YellowButton, self.BlueButton]
            QTimer.singleShot(self.InitialDelay, lambda: self.FlashButtonOn("BlindModeInitial"))
        else:
            self.AddMove()
            QTimer.singleShot(self.InitialDelay, self.FlashButtonOn)

    #Adds move to the list NeededMoves
    def AddMove(self, Button = None):
        self.PlayerMoves = []
        self.SetButtonState(False)
        if Button == None:
            Possibilities = [self.GreenButton, self.RedButton, self.YellowButton, self.BlueButton]        
            Button = random.choice(Possibilities)
        self.NeededMoves.append(Button)
        
    #On a button press, flash colour
    def PlayerButtonPressed(self, Button):
        Button.setStyleSheet(f"background-color: {Button.FlashColour};")
        threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound(Button.SoundName))).start() 
        self.PlayerMoves.append(Button)
        
    def PlayerButtonReleased(self, Button):
        Button.setStyleSheet(f"background-color: {Button.Colour};")
        SequenceValid = True
        LastPlayerMoveIndex = len(self.PlayerMoves) - 1
        
        #UserExtraMoveNeeded can only be true if playing in multiplayer mode and the user needs to add an extra move to the list 
        if self.UserExtraMoveNeeded == False:
            if self.PlayerMoves[LastPlayerMoveIndex] != self.NeededMoves[LastPlayerMoveIndex]:
                SequenceValid = False
                self.IndexFail = LastPlayerMoveIndex
        
        #If user has clicked all the required moves in the sequence or has clicked the extra move in multiplayer mode
        if (len(self.PlayerMoves) == len(self.NeededMoves) and SequenceValid == True) or self.UserExtraMoveNeeded == True:
            #Multiplayer mode, user has clicked on their extra move
            if self.UserExtraMoveNeeded == True:
                threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound("NextPlayer.mp3"))).start()
                self.PlayerMoves = []
                self.NeededMoves.append(Button)
                self.UserExtraMoveNeeded = False
            
            #All move in sequence completed, the user's next click will act as their extra move
            elif self.GameMode == "Multiplayer":
                self.UserExtraMoveNeeded = True
                
            else:
                #Not in Multiplayer mode, add a move to the sequence
                self.AddMove()
                QTimer.singleShot(self.InitialDelay, self.FlashButtonOn)
            
            #All required moves made, move onto next round
            if self.UserExtraMoveNeeded == False:
                self.Round = self.Round + 1
                self.RoundLabel.setText(f"Round: {self.Round}")
            
        if SequenceValid == False:
            self.GameOver()
    
    def FlashButtonOn(self, Mode="Normal", Counter = 0):
        #Flashes the correct answer upon a mistake, ends the game
        if Mode == "GameOver":
            MovesList = self.GameOverMoves
            FlashTime = self.GameOverFlashDelay
            
            #Varying sound effects depending on user score (0 points has a different sound)
            if Counter == 0:
                if self.Round == 1:
                    threading.Thread(target = lambda: playsound("ZeroPoints.mp3")).start()
                else:                    
                    threading.Thread(target = lambda: playsound("GameOver.mp3")).start()

        elif Mode == "BlindModeInitial":
            #Sets up the blind mode initiation sequence
            MovesList = self.BlindModeSequence
            FlashTime = self.FlashOffDelay
        else:
            #Sets up the 'Classic Gamemode' sequence
            MovesList = self.NeededMoves
            FlashTime = self.FlashOffDelay * max(0.4, 1 - ((len(MovesList) // 10) / 5))
                
        #Flash button and play sound depending on game mode
        if Counter < len(MovesList):
            #Set button to the next move in the sequence
            Button = MovesList[Counter]

            if self.GameMode != "Blind" or Mode == "BlindModeInitial" or Mode == "GameOver":
                Button.setStyleSheet(f"background-color: {Button.FlashColour};")
            
            if Mode != "GameOver":
                threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound(Button.SoundName))).start()
                
            Counter = Counter + 1
            QTimer.singleShot(FlashTime, lambda: self.FlashButtonOff(Mode, Button, Counter))
        
        else:
            if Mode == "GameOver":
                #Button has already been flashed, keep flash colour. Reset menus
                QTimer.singleShot(0, lambda: MovesList[0].setStyleSheet(f"background-color: {MovesList[0].FlashColour};"))
                self.StartButton.setEnabled(True)
                self.StartButton.setStyleSheet("background-color: white;")
                self.toolbar.setEnabled(True)
            elif Mode == "BlindModeInitial":
                #Play sound to denote end of blind mode animations
                threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound("BlindStart.wav"))).start()
                self.AddMove()
                QTimer.singleShot(self.InitialDelay, self.FlashButtonOn)
            else:
                self.SetButtonState(True)
            
    
    def FlashButtonOff(self, Mode, Button, Counter):
        #Set Delay
        if Mode == "GameOver":
            FlashTime = self.GameOverFlashDelay
        else:
            FlashTime = self.FlashOnDelay * max(0.4, 1 - ((len(self.NeededMoves) // 10) / 5))
        
        #Reverts the colour back to normal
        if self.GameMode != "Blind" or Mode == "BlindModeInitial" or Mode == "GameOver":
            Button.setStyleSheet(f"background-color: {Button.Colour};")
            
        QTimer.singleShot(FlashTime, lambda: self.FlashButtonOn(Mode, Counter))
        
    def GameOver(self):
        #Game Over Sequence
        Button = self.NeededMoves[self.IndexFail]
        self.SetButtonState(False)
        print("You Idiot")
        self.GameOverMoves = [Button, Button, Button]
        self.FlashButtonOn("GameOver")
        
class ColouredButton(QPushButton):
    #Defining the Buttons
    def __init__(self, Colour, FlashColour, SoundName):       
        super().__init__()
        self.Colour = Colour
        self.FlashColour = FlashColour
        self.SoundName = SoundName
        self.setFixedSize(175, 175)
        self.setStyleSheet(f"background-color: {self.Colour};")
        self.pressed.connect(lambda: window.PlayerButtonPressed(self))
        self.released.connect(lambda: window.PlayerButtonReleased(self))
        
#If I import this in future to a different program
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

