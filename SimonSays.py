import sys, random
from playsound import playsound
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QMessageBox
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #Scales to other devices

class MainWindow(QMainWindow):
    def __init__(self):
        self.NeededMoves = []
        #self.PlayerMoves = []
    
        super().__init__()
        self.setWindowTitle("Shimon Says")
        self.setStyleSheet(f"background-color: black;")
        
        self.MainLayout = QGridLayout()

        self.GreenButton = ColouredButton("green", "#57D658","Green.wav")
        self.MainLayout.addWidget(self.GreenButton, 0, 0)
        
        self.RedButton = ColouredButton("#CC0000", "#FF0000", "Red.wav")
        self.MainLayout.addWidget(self.RedButton, 0, 1)

        self.YellowButton = ColouredButton("#CCCC00", "#FFFF00", "Yellow.wav") #default, flash
        self.MainLayout.addWidget(self.YellowButton, 1, 0)
        
        self.BlueButton = ColouredButton("#0000B2", "#0000FF", "Blue.wav")
        self.MainLayout.addWidget(self.BlueButton, 1, 1)        
        
        #dummy widget pyqt5 needs it
        widget = QWidget()
        widget.setLayout(self.MainLayout)
        self.setCentralWidget(widget)
        
        self.ComputerRound()
    
    def ComputerRound(self):
        self.PlayerMoves = []
        self.setEnabled(False)
        Possibilities = [self.YellowButton, self.BlueButton, self.RedButton, self.GreenButton]        
        Choice = random.choice(Possibilities)
        self.NeededMoves.append(Choice)
        DelayTimer = 1000
        for x in self.NeededMoves:
            x.FlashButton(DelayTimer)
            DelayTimer = DelayTimer + 900
        
        QTimer.singleShot(DelayTimer, lambda: self.setEnabled(True))
    
    def PlayerPushButton(self, Button):
        SequenceValid = True
        self.PlayerMoves.append(Button)
        Button.FlashButton(0)
        
        for i in range(len(self.PlayerMoves)):
            if self.PlayerMoves[i] != self.NeededMoves[i]:
                SequenceValid = False
        
        if len(self.PlayerMoves) == len(self.NeededMoves) and SequenceValid == True:
            self.ComputerRound()
            
        if SequenceValid == False:
            self.GameOver()
    
    def GameOver(self):
        self.setEnabled(False)
        Text = "<h2>Game Over!</h2><p style='text-align:center;font-size:18px'>you idiot</p>"
        PlayAgain = QMessageBox()
        PlayAgain.setWindowTitle("Restart Game")
        PlayAgain.setText(Text)
        PlayAgain.setWindowFlags(Qt.WindowStaysOnTopHint)
        PlayAgain.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        PlayAgain.setIcon(QMessageBox.Question) 
        if PlayAgain.exec_() == QMessageBox.Yes:
            print("new game")
        # Display Score
        
        
class ColouredButton(QPushButton):
    def __init__(self, Colour, FlashColour, SoundName):
        super().__init__()
        self.Colour = Colour
        self.FlashColour = FlashColour
        self.SoundName = SoundName
        self.setFixedSize(200, 200)
        self.setStyleSheet(f"background-color: {self.Colour};")
        self.clicked.connect(lambda: window.PlayerPushButton(self))
    
    def FlashButton(self, delay):
        QTimer.singleShot(delay, lambda: self.setStyleSheet(f"background-color: {self.FlashColour};"))
        QTimer.singleShot(delay + 100,lambda: playsound(self.SoundName))
        QTimer.singleShot(delay + 500, lambda: self.setStyleSheet(f"background-color: {self.Colour};"))

#If I import this in future to a different program
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())