#TODO:
#remove self.counter
#disable toolbar during a game
#Points
#COMMENT CODE
#Fixed Window Size
#rafi !> ben
#------------
#Laugh at 0 points
#new graphical shpill

import sys, random, threading
from playsound import playsound
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QMessageBox, QToolBar, QLabel, QComboBox
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #Scales to other devices

class MainWindow(QMainWindow):
    def __init__(self):
        self.InitialDelay = 1000
        self.FlashOnDelay = 250
        self.FlashOffDelay = 650
        self.SoundDelay = 20
        self.GameMode = "Classic"
        
        super().__init__()
        self.setWindowTitle("Simon Game")
        self.setStyleSheet(f"background-color: black;")
        
        self.toolbar = QToolBar("MainBar")
        #self.toolbar.setStyleSheet(f"background-color: ;")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.toggleViewAction().setEnabled(False)
        
        GameModeLabel = QLabel("GameMode")
        GameModeLabel.setFont(QFont("Arial", 10))
        GameModeLabel.setStyleSheet("color: white;")
        GameModeLabel.setContentsMargins(10, 5, 5, 5)
        self.toolbar.addWidget(GameModeLabel)
        
        self.GameModeCombo = QComboBox()
        self.GameModeCombo.addItems(["Classic", "Multiplayer", "Blind"])
        self.GameModeCombo.setStyleSheet("font-size: 10pt; selection-background-color: black; color: white;")
        self.GameModeCombo.currentTextChanged.connect(self.GameModeChanged)
        self.toolbar.addWidget(self.GameModeCombo)
        
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
        
        self.ChangeButtonState(False)
        
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
    
    def ChangeButtonState(self, State):
        self.GreenButton.setEnabled(State)
        self.RedButton.setEnabled(State)
        self.YellowButton.setEnabled(State)
        self.BlueButton.setEnabled(State)
    
    def ResetButtonFlash(self):
        self.GreenButton.setStyleSheet(f"background-color: {self.GreenButton.Colour};")
        self.RedButton.setStyleSheet(f"background-color: {self.RedButton.Colour};")
        self.YellowButton.setStyleSheet(f"background-color: {self.YellowButton.Colour};")
        self.BlueButton.setStyleSheet(f"background-color: {self.BlueButton.Colour};")
        
    def StartGame(self):
        self.StartButton.setEnabled(False)
        self.StartButton.setStyleSheet("background-color: #C2C2C2;")
        self.ResetButtonFlash()
        self.NeededMoves = []
        self.PlayerMoves = []
        
        if self.GameMode == "Blind":
            self.BlindModeSequence = [self.GreenButton, self.RedButton, self.YellowButton, self.BlueButton]
            self.BlindModeFlashOn(0)
        else:
            self.AddMove()
            QTimer.singleShot(self.InitialDelay, self.FlashButtonOn)
                
    def BlindModeFlashOn(self, Counter):
        if Counter < len(self.BlindModeSequence):
            Button = self.BlindModeSequence[Counter]
            threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound(Button.SoundName))).start() 
            Button.setStyleSheet(f"background-color: {Button.FlashColour};")
            Counter = Counter + 1
            QTimer.singleShot(self.FlashOffDelay, lambda: self.BlindModeFlashOff(Button, Counter))
        else:
            threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound("BlindStart.wav"))).start()
            self.AddMove()
            QTimer.singleShot(self.InitialDelay, self.FlashButtonOn)
    
    def BlindModeFlashOff(self, Button, Counter):
        Button.setStyleSheet(f"background-color: {Button.Colour};")
        QTimer.singleShot(self.FlashOnDelay + 100, lambda: self.BlindModeFlashOn(Counter))
        
    def AddMove(self, Button = None):
        self.PlayerMoves = []
        self.ChangeButtonState(False)
        if Button == None:
            Possibilities = [self.GreenButton, self.RedButton, self.YellowButton, self.BlueButton]        
            Button = random.choice(Possibilities)
        self.NeededMoves.append(Button)
        self.NeededMovesIter = iter(self.NeededMoves)
        
    def PlayerButtonPressed(self, Button):
        Button.setStyleSheet(f"background-color: {Button.FlashColour};")
        threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound(Button.SoundName))).start() 
        self.PlayerMoves.append(Button)
        
    def PlayerButtonReleased(self, Button):
        SequenceValid = True
        Button.setStyleSheet(f"background-color: {Button.Colour};")
        
        for i in range(len(self.PlayerMoves)):
            if self.PlayerMoves[i] != self.NeededMoves[i]:
                SequenceValid = False
                self.IndexFail = i
        
        if len(self.PlayerMoves) == len(self.NeededMoves) and SequenceValid == True:
            self.AddMove()
            QTimer.singleShot(self.InitialDelay, self.FlashButtonOn)
            
        if SequenceValid == False:
            self.GameOver()
    
    def FlashButtonOn(self):
        try:
            Button = next(self.NeededMovesIter)
        except StopIteration:
            self.ChangeButtonState(True)
        else:
            FlashTime = self.FlashOffDelay * max(0.4, 1 - ((len(self.NeededMoves) // 10) / 5))
            if self.GameMode != "Blind":
                Button.setStyleSheet(f"background-color: {Button.FlashColour};")
            threading.Thread(target = QTimer.singleShot(self.SoundDelay, lambda: playsound(Button.SoundName))).start() 
            QTimer.singleShot(FlashTime, lambda: self.FlashButtonOff(Button))
    
    def FlashButtonOff(self, Button):
        FlashTime = self.FlashOnDelay * max(0.4, 1 - ((len(self.NeededMoves) // 10) / 5))
        if self.GameMode != "Blind":
            Button.setStyleSheet(f"background-color: {Button.Colour};")
        QTimer.singleShot(FlashTime, lambda: self.FlashButtonOn())
        
    def GameOver(self):
        Button = self.NeededMoves[self.IndexFail]
        self.ChangeButtonState(False)
        print("You Idiot")
        self.Counter = 1
        self.GameOverDelay = 0
        self.GameOverFlashOn(Button)

    def GameOverFlashOn(self, Button):
        if self.Counter < 3:
            if self.Counter == 1:
                threading.Thread(target = lambda: playsound("GameOver.mp3")).start()
            Button.setStyleSheet(f"background-color: {Button.FlashColour};")
            self.Counter = self.Counter + 1
            self.GameOverDelay = self.GameOverDelay + 100
            QTimer.singleShot(self.GameOverDelay, lambda: self.GameOverFlashOff(Button))
        else:
            QTimer.singleShot(0, lambda: Button.setStyleSheet(f"background-color: {Button.FlashColour};"))
            self.StartButton.setEnabled(True)
            self.StartButton.setStyleSheet("background-color: white;")
    
    def GameOverFlashOff(self, Button):
        Button.setStyleSheet(f"background-color: {Button.Colour};")
        QTimer.singleShot(self.GameOverDelay + 100, lambda: self.GameOverFlashOn(Button))

#         PlayAgain = QMessageBox()
#         PlayAgain.setWindowTitle("Restart Game")
#         PlayAgain.setText(Text)
#         PlayAgain.setWindowFlags(Qt.WindowStaysOnTopHint)
#         PlayAgain.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
#         PlayAgain.setIcon(QMessageBox.Question) 
#         if PlayAgain.exec_() == QMessageBox.Yes:
#             print("new game")
        # Display Score    
        
class ColouredButton(QPushButton):
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
