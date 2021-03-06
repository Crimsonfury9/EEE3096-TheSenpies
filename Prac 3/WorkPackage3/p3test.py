# Import libraries
from math import floor
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
from time import sleep

# some global variables that need to change as we run the program
finishGame = None  # set if the user wins or ends the game
numGuess = 0 #number of guesses
value=1     #randomly generated number
buttonHold=0    #counter for when submit button is pressed
guess=0         #the number the user guessed
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
pwmLed = None
pwmBuzz = None  
play= "Start"
eeprom = ES2EEPROMUtils.ES2EEPROM()
eeprom.clear(2048) #clear the eeprom
eeprom.populate_mock_scores() #populate the eeprom with mock scores


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global finishGame
    global value
    global numGuess
    global pwmLed
    global pwmBuzz
    global play
    finishGame=False
   # print(eeprom.read_block(1,4))
   # print(eeprom.read_block(0,4))
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        play="Scores"
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
       # finishGame=False
        os.system('clear')
        play="Begin"
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        #print('Hello')
        value = generate_number()
        while not finishGame:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    #print(raw_data)
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    raw_data.sort(key=lambda x: x[1])
    topThree=0
    while(topThree<3):
        print("{} - {} took {} guesses".format(topThree+1, raw_data[topThree][0], raw_data[topThree][1]))
        topThree+=1
    


# Setup Pins
def setup():
    global pwmLed
    global pwmBuzz
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(LED_value, GPIO.OUT)
    GPIO.output(LED_value, False)
    #GPIO.setup(power, GPIO.OUT)
    GPIO.setup(LED_accuracy,GPIO.OUT)
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)   #setup a button of type pull up 
    GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)   #setup a button of type pull up 
   # GPIO.output(power,1)
    # Setup PWM channels
    pwmBuzz = GPIO.PWM(buzzer, 1)
    pwmBuzz.ChangeDutyCycle(0)
    pwmLed = GPIO.PWM(LED_accuracy, 1)
    pwmLed.ChangeDutyCycle(0)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=100)
    
    


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)   #reading the first register of the eeprom
    # Get the scores
    arrScores = []
    scores=[]
    for i in range(1,(score_count+1)):  #loops through the blocks of the eeprom with the scores
        arrScores.append(eeprom.read_block(i,4)) #storage of the scores found
    # convert the codes back to ascii
        x=''
        for q in range(len(arrScores[i-1])):
            if q<3:
                x +=chr(arrScores[i-1][q])
        scores.append([x, arrScores[i-1][3]])        
    # return back the results
    return score_count, scores


# Save high scores
def save_scores(newScore):
    # fetch scores
    totalScores,arrSave = fetch_scores()
    totalScores+=1
    #print(totalScores)
    #eeprom.clear(2048)
    eeprom.write_block(0, [totalScores])
    # include new score
    arrSave.append(newScore)
   # print(arrSave)
    # sort
    arrSave.sort(key=lambda x: x[1])
    #data_to_write=[]
    for i, score in enumerate(arrSave):
        data_to_write=[]
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
        eeprom.write_block(i+1, data_to_write)
    # update total amount of scores
    # write new scores


# Generate guess number
def generate_number():
    return random.randint(1, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global guess
    global play
    if (GPIO.input(channel)==0 and play== "Begin"):

        if (guess>=7):
                guess=1
                
        else:
                guess+=1    

            
            
        # Increase the value shown on the LEDs
        for i in range(1,guess+1):
            if i in [1,4,7]:
                GPIO.output(11,GPIO.HIGH)
                sleep(0.5)
                GPIO.output(11,GPIO.LOW)
            elif i in [2,5,8]:
                GPIO.output(13,GPIO.HIGH)
                sleep(0.5)
                GPIO.output(13,GPIO.LOW)
            elif i in [3,6]:
                GPIO.output(15,GPIO.HIGH)
                sleep(0.5)
                GPIO.output(15,GPIO.LOW)
        

def start():
    global buttonHold
    buttonHold = time.time()

def stop():
    global buttonHold
    return time.time() - buttonHold   

    


# Guess button
def btn_guess_pressed(channel):
    global play
    global value
    global guess
    global finishGame
    global numGuess
    global buttonHold
    #global pwmBuzz
    #global pwmLed
    start()

    w=0
    while (GPIO.input(channel)==0):
        sleep(0.05)
    if (play== "Begin"):    
        buttonRelease=stop()  

        currentValue= value
        currentGuess = guess
        diff=abs(currentValue-currentGuess)

        if (buttonRelease>=2):
            #welcome()
            play="Start"
            #GPIO.cleanup()
            finishGame=True
            numGuess = 0 
            buttonHold=0    #counter for when submit button is pressed
            guess=0         
            pwmLed.ChangeDutyCycle(0)
            pwmBuzz.ChangeDutyCycle(0)
            GPIO.output(LED_value, False)
            
            
        else:
            if (diff>0 and guess!=0):
                numGuess+=1
                accuracy_leds()
                trigger_buzzer()
               # print("{}-is your guess".format(numGuess))
            else:
                #print("{}-is your guess".format(numGuess))
                #GPIO.cleanup()
                pwmLed.ChangeDutyCycle(0)
                pwmBuzz.ChangeDutyCycle(0)
                GPIO.output(LED_value, False)
                print("Well done champion, you the winnnneerr!! Whooo ")
               # print(value)
                name = input("Please enter your name: ")
                if (len(name)>3):
                    name=name[0]+name[1]+name[2]
                save_scores([name,numGuess+1])

                #welcome()
                play="Start"
                numGuess = 0 
                buttonHold=0    #counter for when submit button is pressed
                guess=0         
                finishGame=True

            




        



    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
   
   

# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global guess
    global value
    global pwmLed
    pwmLed.stop()
    accuValue=value
    accuGuess=guess
    if (accuGuess>accuValue):
        dutycycle = ((8-accuGuess)/(8-accuValue))*100
    else: 
        dutycycle = (accuGuess/accuValue)*100
    pwmLed.ChangeDutyCycle(dutycycle)
    pwmLed.start(dutycycle)

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global value
    global guess
    global pwmBuzz

    pwmBuzz.start(50)
    buzzerValue=value
    buzzerGuess=guess
    difference=abs(buzzerValue-buzzerGuess)
    if (difference==3):
        frequency=1
        pwmBuzz.ChangeFrequency(frequency)
    elif (difference==2):
        frequency=2
        pwmBuzz.ChangeFrequency(frequency)
    elif (difference==1):
        frequency=4
        pwmBuzz.ChangeFrequency(frequency)
    else:
        pwmBuzz.stop()








if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            #setup()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
