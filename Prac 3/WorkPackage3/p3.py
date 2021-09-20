# Import libraries
from math import floor
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
from time import sleep
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
guess = 0
buttBounce = 0
value = 0
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
buzzPWM = None
ledPWM = None


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
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        display_scores()
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores():
    # print the scores to the screen in the expected format
    print("test")
    score_count, scores = fetch_scores()
    print("test2")
    print("There are {score_count} scores. Here are the top 3!".format(score_count))
    for i in range(1,4):
        j = i
        Score = scores[i-1]
        Name = Score[0]
        points = Score[1]
        print(str(j)+"- "+Name+" took "+str(points)+" guesses")
    # print out the scores in the required format

    pass


def my_callback(channel):
    global buttonStatus
    start_time = time.time()

    while GPIO.input(channel) == 0: 
        pass

    buttonTime = time.time() - start_time    

    if buttonTime >= 4:
        buttBounce = 0 
    elif buttonTime >= .1: 
        buttBounce = 1



# Setup Pins
def setup():
    eeprom.clear(2048)
    eeprom.populate_mock_scores()
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(LED_value, GPIO.OUT,initial = GPIO.LOW)
    GPIO.setup(LED_accuracy,GPIO.OUT,initial = GPIO.LOW)
    GPIO.setup(buzzer,GPIO.OUT,initial = GPIO.LOW)
    GPIO.setup(btn_increase,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(btn_submit,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
    GPIO.output(LED_accuracy,1)
    GPIO.output(LED_value,0)
    GPIO.output(buzzer,0)
    # Setup PWM channels
    buzzPWM = GPIO.PWM(buzzer,1)
    ledPWM = GPIO.PWM(LED_accuracy,1)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=my_callback, bouncetime=500)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=my_callback, bouncetime=500)
    pass



# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_block(0,1)
    # Get the scores
    scores = None
    # convert the codes back to ascii 
    for i in range(1,score_count(0)+1):
        temp = eeprom.read_block(i,4)
        print(temp)
        tempArr = [chr(temp[0])+chr(temp[1])+chr(temp[2]),str(temp[3])]
        scores.append(tempArr)
    scoresSorted = sorted(scores,key=lambda x: x[1])
    # for i in range(1,score_count):
    #     temp = eeprom.read_block(i,4)
    #     lstName[i-1] = chr(temp[0])+chr(temp[1])+chr(temp[2])
    #     lstScore[i-1] = temp[3]
    # # return back the results
    # for i in len(lstName):
    #     for j in len(lstScore):
    #         if lstScore[i] > lstScore[j]:
    #             temp1 = lstScore[i]
    #             lstScore[i] = lstScore[j]
    #             lstScore[j] = temp1

    #             temp2 = lstName[i]
    #             lstName[i] = lstName[j]
    #             lstName[j] = temp2


    return score_count, scoresSorted


# Save high scores
def save_scores(name,points):
    # fetch scores
    score_count, scores =fetch_scores()
    # include new score
    scores.append([name,points])
    # sort
    scoresSorted = sorted(scores,key=lambda x: x[1])
    # update total amount of scores
    score_count = score_count+1
    # write new scores
    eeprom.write_block(0,[score_count,0,0,0])
    for i in range(1,score_count+1):
        tempArr = [ord(name[0])+ord(name[1])+ord(name[2]),points]
        eeprom.write_block(i,tempArr)
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    led1 = 0
    led2 = 0
    led3 = 0
    while True:
        if GPIO.input(channel) == GPIO.HIGH:
            guess = guess+1
            if guess == 9:
                guess = 0
        for i in range(1,guess+1):
            if i in [1,4,7]:
                for j in range(1,floor(i/2)+1):
                    GPIO.output(11,GPIO.HIGH)
                    sleep(1)
                    GPIO.output(11,GPIO.LOW)
            if i in [2,5,8]:
                for j in range(1,floor(i/2)+1):
                    GPIO.output(13,GPIO.HIGH)
                    sleep(1)
                    GPIO.output(13,GPIO.LOW)
            if i in [3,6]:
                for j in range(1,floor(i/2)+1):
                    GPIO.output(15,GPIO.HIGH)
                    sleep(1)
                    GPIO.output(15,GPIO.LOW)
            sleep(3)
        
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    numGuesses=0
    while True:
        if GPIO.input(channel) == GPIO.HIGH:
            if buttBounce == 1:
                GPIO.cleanup()
                menu()
            else:
                if guess == value:
                    GPIO.output(LED_accuracy,GPIO.LOW)
                    GPIO.output(LED_value,GPIO.LOW)
                    GPIO.output(buzzer,GPIO.LOW)
                    buzzPWM.stop()
                    ledPWM.stop()
                    Name = input("Impressive! Let's add you to our hall of fame, what's your Name? (Three Characters only)")
                    if len(Name) != 3:
                        while len(Name) != 3:
                            Name = input("Sorry your name isn't of sufficient lenght, please re-enter!(Three Characters only)")
                    
                    save_scores(Name,numGuesses)
                    menu()
                elif guess <= value+3 and guess >=value-3 and guess != value:
                    print("You're really close! Try again!")
                    trigger_buzzer()
                    accuracy_leds()
                else:
                    print("Sorry you're way off! Try again!")
                    
                            
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
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    ledPWM.start(0)
    if guess > value:
        ledPWM.ChangeDutyCycle(round(((8-guess)/(8-value))*100))
    else:
        ledPWM.ChangeDutyCycle(round((guess/value)*100))
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    buzzPWM.start(50)
    if guess == value-3 or guess ==value+3:
        buzzPWM.ChangeFrequency(1)
    elif guess == value-2 or guess ==value+2:
            buzzPWM.ChangeFrequency(0.5)
    elif guess == value-1 or guess ==value+1:
            buzzPWM.ChangeFrequency(0.25)
        
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
